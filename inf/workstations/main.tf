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
variable "subnet_id" {}

# Find out all the subnet CIDR blocks
locals {
  subnets = toset([for ws in var.instances : ws.cidr])
}

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
resource "aws_instance" "workstation" {
  for_each               = var.instances
  ami                    = "ami-08116b9957a259459" # Pinned Ubuntu 22.04
  instance_type          = "t3.micro"
  key_name               = var.ssh_key_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.sg-workstation[each.key].id]
  private_ip             = each.value.ip

  user_data = <<-EOF
#cloud-config
users:
  - default
  - name: ubt
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock-passwd: false
    ssh_pwauth: True
    chpasswd: { expire: False }
    groups: users, admin
    home: /home/ubuntu
    shell: /bin/bash
    passwd: $6$9lMlqCh9w0fd.2yY$VE/Agz52sDVgQmyKBt710soF6JfR1XQCe8V5uO2.scY1mX5VNDDDHo.Wg2QybAWBMRZwCPZsQTkLK3EWn9dz2.

    EOF

  tags = {
    Name = "${var.vpc_name}-${each.key}"
  }
}
