resource "aws_s3_bucket" "ckpts" { bucket = "hep-ckpts-${random_id.s.hex}" }
