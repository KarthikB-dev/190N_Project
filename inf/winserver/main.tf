variable "vpc_id" {}
variable "vpc_name" {}
variable "vpc_cidr" {}
variable "instances" {
  default = {}
  type = map(object({
    cidr = string
    ip   = string
  }))
}
variable "ssh_key_name" {
}

variable "router_nic_id" {
}

variable "tls_private_key" {
}
variable "subnet_id" {}

resource "aws_security_group" "sg-workstation" {
  for_each = var.instances
  name     = "${var.vpc_name}_sg_${each.key}"
  vpc_id   = var.vpc_id
  ingress {
    description = "Allow ingress from private subnet"
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # "-1" means all protocols
    cidr_blocks = [var.vpc_cidr]
  }

  # Outward Network Traffic for the instance
  egress {
    description = "allow all egress traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Fianlly, launch the workstations
resource "aws_instance" "winserver22" {
  for_each               = var.instances
  ami                    = "ami-0845068028e672a07" # Pinned Ubuntu 22.04
  instance_type          = "t3.small"
  key_name               = var.ssh_key_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.sg-workstation[each.key].id]
  private_ip             = each.value.ip
  get_password_data      = true

  user_data = <<-EOF
    <powershell>
    echo "Hello from Windows Server 2022" > C:\hello.txt
    # Configure WinRM for Ansible
    winrm quickconfig -q
    winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="1024"}'
    winrm set winrm/config '@{MaxTimeoutms="1800000"}'
    winrm set winrm/config/service '@{AllowUnencrypted="true"}'
    winrm set winrm/config/service/auth '@{Basic="true"}'
    Set-Item -Force WSMan:\localhost\Service\Auth\Basic $true
    Set-Item -Force WSMan:\localhost\Service\AllowUnencrypted $true
    Enable-PSRemoting -Force

    # Create a self-signed certificate for WinRM over HTTPS
    New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "Cert:\LocalMachine\My"
    $certThumbprint = (Get-ChildItem Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*CN=localhost*" }).Thumbprint
    winrm create winrm/config/Listener?Address=*+Transport=HTTPS "@{Hostname=`"localhost`";CertificateThumbprint=`"$certThumbprint`"}"
    
    # Enable firewall rules for WinRM
    # Enable-NetFirewallRule -Name "WINRM-HTTP-In-TCP-PUBLIC"
    # Enable-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-PUBLIC"
    # The above two lines errored, now trying https://github.dev/wardviaene/terraform-course/blob/master/demo-2b/windows-instance.tf

    netsh advfirewall firewall add rule name="WinRM 5985" protocol=TCP dir=in localport=5985 action=allow
    netsh advfirewall firewall add rule name="WinRM 5986" protocol=TCP dir=in localport=5986 action=allow
    
    Write-Host "WinRM configured successfully for Ansible"
    echo "WinRM configured successfully for Ansible" >> C:\hello.txt
    </powershell>
    EOF

  tags = {
    Name = "${var.vpc_name}-${each.key}"
  }
}
output "winserver22_passwords" {
  value = { for key, value in aws_instance.winserver22 : key => rsadecrypt(aws_instance.winserver22[key].password_data, var.tls_private_key) }
}
