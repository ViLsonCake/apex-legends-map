terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
  }

  # Backend blocks can't use variables. The bucket name is account-specific, so pass it at init:
  #   terraform init -backend-config="bucket=<state_bucket output of infra/bootstrap>"
  # CI also passes key and region with -backend-config, which override the values below.
  backend "s3" {
    key          = "apex-legends-map-bot/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
  }
}
