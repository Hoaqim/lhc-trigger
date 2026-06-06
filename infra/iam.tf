data "aws_iam_policy_document" "ckpt_s3" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.ckpts.arn}/*"]
  }
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.ckpts.arn]
  }
}

resource "aws_iam_policy" "ckpt_s3" {
  name   = "hep-ckpt-s3"
  policy = data.aws_iam_policy_document.ckpt_s3.json
}

module "training_irsa" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version   = "~> 5.0"
  role_name = "hep-training-irsa"
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:training-sa"]
    }
  }
  role_policy_arns = { s3 = aws_iam_policy.ckpt_s3.arn }
}

output "training_role_arn" { value = module.training_irsa.iam_role_arn }