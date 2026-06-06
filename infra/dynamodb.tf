resource "aws_dynamodb_table" "stats" {
  name         = "hep-stats"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  attribute {
    name = "pk"
    type = "S"
  }
}
