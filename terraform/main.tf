# Configuração principal do Terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "synapse-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "eu-west-1"
  }
}

# Configuração do ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "synapse-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Configuração do RDS
resource "aws_db_instance" "postgres" {
  identifier        = "synapse-db"
  engine            = "postgres"
  engine_version    = "14.5"
  instance_class    = "db.t3.medium"
  allocated_storage = 20
  
  backup_retention_period = 7
  multi_az               = true
  skip_final_snapshot    = false
  
  db_name  = "synapse"
  username = var.db_username
  password = var.db_password
}

# Configuração do Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "synapse-cache"
  engine              = "redis"
  node_type           = "cache.t3.micro"
  num_cache_nodes     = 1
  parameter_group_name = "default.redis6.x"
  port                = 6379
} 