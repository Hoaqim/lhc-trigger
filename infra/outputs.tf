output "cluster_name" { value = module.eks.cluster_name }
output "msk_brokers"  { value = aws_msk_cluster.events.bootstrap_brokers_tls }
output "ckpt_bucket"  { value = aws_s3_bucket.ckpts.bucket }
output "ecr_repos"    { value = { for k, r in aws_ecr_repository.r : k => r.repository_url } }
output "training_role_arn" { value = module.training_irsa.iam_role_arn }