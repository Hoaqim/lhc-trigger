resource "aws_ecr_repository" "r" {
  for_each = toset(["training", "streaming", "dashboard", "mlflow"])
  name     = "hep-${each.key}"
}