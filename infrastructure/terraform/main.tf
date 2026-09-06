module "networking" {
  source      = "./modules/networking"
  environment = var.environment
  aws_region  = var.aws_region
}

module "eks" {
  source      = "./modules/eks"
  environment = var.environment
  subnet_ids  = module.networking.private_subnet_ids
}

module "rds" {
  source      = "./modules/rds"
  environment = var.environment
  subnet_ids  = module.networking.private_subnet_ids
}
