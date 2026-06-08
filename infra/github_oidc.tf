variable "github_repo" {
  description = "owner/repo"
  type        = string
  default = "Hoaqim/lhc-trigger"
}

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "gha_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"
    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "gha_deploy" {
  name               = "hep-gha-deploy"
  assume_role_policy = data.aws_iam_policy_document.gha_assume.json
}

resource "aws_iam_role_policy_attachment" "gha_admin" {
  role       = aws_iam_role.gha_deploy.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"   # simplest for a course project
}

output "gha_role_arn" {
  value = aws_iam_role.gha_deploy.arn
}
