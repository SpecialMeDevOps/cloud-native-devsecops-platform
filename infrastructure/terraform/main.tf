module "networking" {
  source               = "./modules/networking"
  environment          = var.environment
  aws_region           = var.aws_region
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  single_nat_gateway   = var.single_nat_gateway
}

module "eks" {
  source             = "./modules/eks"
  environment        = var.environment
  subnet_ids         = module.networking.private_subnet_ids
  vpc_id             = module.networking.vpc_id
  cluster_version    = var.cluster_version
  node_instance_type = var.node_instance_type
  node_desired_size  = var.node_desired_size
  node_min_size      = var.node_min_size
  node_max_size      = var.node_max_size
}

module "rds" {
  source                     = "./modules/rds"
  environment                = var.environment
  subnet_ids                 = module.networking.private_subnet_ids
  vpc_id                     = module.networking.vpc_id
  allowed_security_group_ids = [module.eks.node_security_group_id]
  instance_class             = var.rds_instance_class
  engine_version             = var.rds_engine_version
  allocated_storage          = var.rds_allocated_storage
  database_name              = var.rds_database_name
  master_username            = var.rds_master_username
}

module "ecr" {
  source      = "./modules/ecr"
  environment = var.environment
  repository_names = [
    "user-service",
    "product-service",
    "order-service",
    "frontend",
  ]
}

module "s3_cloudfront" {
  source              = "./modules/s3-cloudfront"
  environment         = var.environment
  cloudfront_aliases  = var.cloudfront_aliases
  acm_certificate_arn = var.acm_certificate_arn
  price_class         = var.cloudfront_price_class
}
