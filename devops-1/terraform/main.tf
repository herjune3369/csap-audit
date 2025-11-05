provider "aws" {
  region = "ap-northeast-2"
}

# VPC 생성 (기존 VPC가 없을 경우)
resource "aws_vpc" "main_vpc" {
  count = var.vpc_id == "" ? 1 : 0

  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "devops-1-vpc"
  }
}

# 기존 VPC 사용 (VPC ID가 제공된 경우)
data "aws_vpc" "existing_vpc" {
  count = var.vpc_id != "" ? 1 : 0
  id    = var.vpc_id
}

# VPC ID 결정
locals {
  vpc_id = var.vpc_id != "" ? var.vpc_id : aws_vpc.main_vpc[0].id
}

# 서브넷 생성
resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = local.vpc_id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-northeast-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-a"
  }
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = local.vpc_id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "ap-northeast-2b"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-b"
  }
}

resource "aws_subnet" "private_subnet_c" {
  vpc_id            = local.vpc_id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "ap-northeast-2c"

  tags = {
    Name = "private-subnet-c"
  }
}

resource "aws_subnet" "private_subnet_b" {
  vpc_id            = local.vpc_id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "ap-northeast-2b"

  tags = {
    Name = "private-subnet-b"
  }
}

# NAT Gateway를 위한 EIP
resource "aws_eip" "nat_eip" {
  domain = "vpc"
}

# NAT Gateway
resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet_a.id

  tags = {
    Name = "nat-gateway"
  }
}

# Internet Gateway 생성
# 새 VPC 생성 시에는 항상 생성, 기존 VPC 사용 시에도 생성 시도
# (기존 VPC에 이미 IGW가 있으면 오류 발생 가능 - 이 경우 수동으로 처리 필요)
resource "aws_internet_gateway" "igw" {
  vpc_id = local.vpc_id

  tags = {
    Name = "devops-1-igw"
  }
}


# Route Tables
resource "aws_route_table" "public_rt" {
  vpc_id = local.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_rt_assoc_a" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rt_assoc_b" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table" "private_rt" {
  vpc_id = local.vpc_id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "private-rt"
  }
}

resource "aws_route_table_association" "private_rt_assoc_c" {
  subnet_id      = aws_subnet.private_subnet_c.id
  route_table_id = aws_route_table.private_rt.id
}

resource "aws_route_table_association" "private_rt_assoc_b" {
  subnet_id      = aws_subnet.private_subnet_b.id
  route_table_id = aws_route_table.private_rt.id
}

# RDS 설정
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "devops-1-rds-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_c.id, aws_subnet.private_subnet_b.id]

  tags = {
    Name = "devops-1-rds-subnet-group"
  }
}

# Security Groups
resource "aws_security_group" "web_sg" {
  name        = "devops-1-web-sg"
  description = "Allow SSH, HTTP, and Flask app port"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "alb_sg" {
  name        = "devops-1-alb-sg"
  description = "Allow HTTP to ALB"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "devops-1-alb-sg"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "devops-1-rds-sg"
  description = "Allow MySQL from EC2"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.public_subnet_a.cidr_block, aws_subnet.public_subnet_b.cidr_block]
    description = "Allow MySQL from public subnets"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "devops-1-rds-sg"
  }
}

# RDS 설정
resource "aws_db_instance" "flask_db" {
  identifier              = "devops-1-flask-db"
  engine                  = "mysql"
  engine_version          = "8.0"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  storage_type            = "gp2"
  db_name                 = "saju"
  username                = "admin"
  password                = var.db_password
  skip_final_snapshot     = true
  multi_az                = false
  backup_retention_period = 0

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name

  tags = {
    Name = "devops-1-flask-db"
  }
}

# SSH 키 페어
resource "aws_key_pair" "app_key" {
  key_name_prefix = "saju-app-key-"
  public_key      = var.public_key
}


# EC2 인스턴스 설정
resource "aws_instance" "web1" {
  ami                         = var.ami_id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public_subnet_a.id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.app_key.key_name

  tags = {
    Name = "webserver1"
  }
}

resource "aws_instance" "web2" {
  ami                         = var.ami_id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public_subnet_b.id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.app_key.key_name

  tags = {
    Name = "webserver2"
  }
}

# Load Balancer 설정
resource "aws_lb" "app_lb" {
  name               = "devops-1-app-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]

  tags = {
    Name = "devops-1-app-lb"
  }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "devops-1-app-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = local.vpc_id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    port                = "5000"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
  }

  tags = {
    Name = "devops-1-app-target-group"
  }
}

resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

resource "aws_lb_target_group_attachment" "web1_attach" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.web1.id
  port             = 5000
}

resource "aws_lb_target_group_attachment" "web2_attach" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.web2.id
  port             = 5000
}


