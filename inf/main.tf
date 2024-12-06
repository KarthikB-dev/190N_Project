terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.41.0"
    }
  }
}

variable "linux_instances" {
  default = {
    "ubuntu1" = {
      cidr = "10.114.0.0/16",
      ip   = "10.114.0.61"
    }
    "ubuntu2" = {
      cidr = "10.114.0.0/16",
      ip   = "10.114.0.62"
    }
    "ubuntu3" = {
      cidr = "10.114.0.0/16",
      ip   = "10.114.0.63"
    }
  }
}

variable "windows_instances" {
  default = {
    "winserver1" = {
      cidr = "10.114.0.0/16",
      ip   = "10.114.1.61"
    }
    "winserver2" = {
      cidr = "10.114.0.0/16",
      ip   = "10.114.1.62"
    }
    "winserver3" = {
      cidr = "10.114.0.0/16",
      ip   = "10.114.1.63"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main_vpc" {
  cidr_block = "10.114.0.0/16"
  tags = {
    Name = "190n_main_vpc"
  }
  enable_dns_support   = true
  enable_dns_hostnames = false
}

resource "aws_vpc" "upstream_vpc" {
  cidr_block = "10.154.0.0/16"
  tags = {
    Name = "190n_upstream_vpc"
  }
  enable_dns_support   = true
  enable_dns_hostnames = false
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.upstream_vpc.id
  tags = {
    Name = "190n-internet-gateway"
  }
}

resource "tls_private_key" "rsa_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "key_pair" {
  key_name   = "190n-inf-key"
  public_key = tls_private_key.rsa_key.public_key_openssh
}

resource "local_file" "private_key" {
  content         = tls_private_key.rsa_key.private_key_pem
  filename        = "190n-inf-key/id_rsa"
  file_permission = 0600
}

resource "aws_subnet" "router_lan_subnet" {
  availability_zone = data.aws_availability_zones.available.names[0]
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.114.0.0/16"
  tags = {
    Name = "190n-router-lan-subnet"
  }
}

resource "aws_subnet" "router_wan_subnet" {
  availability_zone = data.aws_availability_zones.available.names[0]
  vpc_id            = aws_vpc.upstream_vpc.id
  cidr_block        = "10.154.0.0/16"
  tags = {
    Name = "190n-router-wan-subnet"
  }
}

resource "aws_route_table" "router-wan-subnet-rt" {
  vpc_id = aws_vpc.upstream_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway.id
  }
  tags = {
    Name = "190n-router-wan-subnet-rt"
  }
}

resource "aws_route_table_association" "router-subnet-rt-association" {
  route_table_id = aws_route_table.router-wan-subnet-rt.id
  subnet_id      = aws_subnet.router_wan_subnet.id
}

resource "aws_route_table" "router-lan-subnet-rt" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block           = "0.0.0.0/0"
    network_interface_id = aws_network_interface.router_lan.id
  }
  tags = {
    Name = "190n-router-lan-subnet-rt"
  }
}

resource "aws_route_table_association" "router-lan-subnet-rt-association" {
  route_table_id = aws_route_table.router-lan-subnet-rt.id
  subnet_id      = aws_subnet.router_lan_subnet.id
}
resource "aws_security_group" "router_wan_sg" {
  vpc_id = aws_vpc.upstream_vpc.id
  ingress {
    description = "Allow ingress from private subnet"
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # "-1" means all protocols
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    description = "Allow ingress for ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow ingress for openvpn"
    from_port   = 1194
    to_port     = 1194
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow ingress for guacamole"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outward Network Traffic for the instance
  egress {
    description = "Allow all egress traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "190n-router-sg"
  }
}

resource "aws_security_group" "router_lan_sg" {
  vpc_id = aws_vpc.main_vpc.id
  ingress {
    description = "Allow all ingress traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all egress traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "router_instance" {
  availability_zone = data.aws_availability_zones.available.names[0]
  depends_on = [
    aws_key_pair.key_pair
  ]
  ami = "ami-08116b9957a259459" # pinned ubuntu version 22.04
  # ami                         = "ami-0da657e96a9bfab37" # esperanza router AMI (built with Packer)
  instance_type = "t3.micro"
  key_name      = aws_key_pair.key_pair.key_name

  network_interface {
    network_interface_id = aws_network_interface.router_wan.id
    device_index         = 0
  }

  network_interface {
    network_interface_id = aws_network_interface.router_lan.id
    device_index         = 1
  }

  tags = {
    Name = "cs190n-router"
  }
  user_data = <<-EOF
#!/bin/bash

# Enable IP forwarding
echo "Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Configure iptables for NAT (Replace eth0 and eth1 with actual interface names)
WAN_INTERFACE="ens5"
LAN_INTERFACE="ens6"

echo "Setting up iptables for NAT..."
iptables -t nat -A POSTROUTING -o $WAN_INTERFACE -j MASQUERADE
iptables -A FORWARD -i $LAN_INTERFACE -o $WAN_INTERFACE -j ACCEPT
iptables -A FORWARD -i $WAN_INTERFACE -o $LAN_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT

# Save iptables rules to make them persistent
# echo "Installing iptables-persistent..."
# apt-get update && apt-get install -y iptables-persistent
# echo "APT finished"
# netfilter-persistent save
# netfilter-persistent reload

echo "NAT configuration complete."
EOF
}

resource "aws_network_interface" "router_wan" {
  subnet_id         = aws_subnet.router_wan_subnet.id
  private_ips       = ["10.154.0.50"]
  security_groups   = [aws_security_group.router_wan_sg.id]
  source_dest_check = false
}

resource "aws_network_interface" "router_lan" {
  subnet_id         = aws_subnet.router_lan_subnet.id
  private_ips       = ["10.114.0.50"]
  security_groups   = [aws_security_group.router_lan_sg.id]
  source_dest_check = false
}

resource "aws_eip" "public_ip" {
  tags = {
    Name = "example-eip"
  }
}

# Associate the Elastic IP with the network interface
resource "aws_eip_association" "public_ip_wan" {
  allocation_id        = aws_eip.public_ip.id
  network_interface_id = aws_network_interface.router_wan.id
}

module "workstations" {
  depends_on    = [aws_instance.router_instance]
  source        = "./workstations"
  instances     = var.linux_instances
  vpc_id        = aws_vpc.main_vpc.id
  vpc_name      = "190n-main"
  vpc_cidr      = "10.114.0.0/16"
  ssh_key_name  = aws_key_pair.key_pair.key_name
  router_nic_id = aws_network_interface.router_lan.id
  subnet_id     = aws_subnet.router_lan_subnet.id
}


module "windowsHosts" {
  depends_on      = [aws_instance.router_instance]
  source          = "./winserver"
  instances       = var.windows_instances
  vpc_id          = aws_vpc.main_vpc.id
  vpc_name        = "190n-main"
  vpc_cidr        = "10.114.0.0/16"
  ssh_key_name    = aws_key_pair.key_pair.key_name
  router_nic_id   = aws_network_interface.router_lan.id
  subnet_id       = aws_subnet.router_lan_subnet.id
  tls_private_key = tls_private_key.rsa_key.private_key_pem
}

locals {
  ssh_conf_header = templatefile("templates/ssh_config_header", {
    host    = "bastion",
    ip      = aws_instance.router_instance.public_ip,
    keyfile = "190n-inf-key/id_rsa"
  })
  ssh_conf_item = join("\n", [for key, value in var.linux_instances : templatefile("templates/ssh_config_item", {
    host    = key,
    ip      = value.ip,
    keyfile = "190n-inf-key/id_rsa"
    bastion = aws_instance.router_instance.public_ip
  })])
  inventory_header = templatefile("templates/inventory_header", {
    ip = aws_instance.router_instance.public_ip
  })
  inventory_static       = "router ansible_host=router ansible_user=ubuntu\n\n"
  inventory_workstations = join("\n", [for key, value in var.linux_instances : "${key} ansible_host=${var.linux_instances[key].ip} ansible_user=ubuntu"])
  windows_inventory = join("\n", [for key, value in var.windows_instances : templatefile("templates/inventory_windows", {
    host     = key,
    ip       = value.ip,
    password = module.windowsHosts.winserver22_passwords[key]
  })])
}

resource "local_file" "ssh_config" {
  content  = "${local.ssh_conf_header}\n\n${local.ssh_conf_item}"
  filename = "190n-inf-key/ssh_config"
}

resource "local_file" "inventory" {
  content  = "${local.inventory_header}\n\n[static]\n${local.inventory_static}\n[linux]\n${local.inventory_workstations}\n\n[win]\n${local.windows_inventory}"
  filename = "190n-inf-key/inventory.ini"
}
