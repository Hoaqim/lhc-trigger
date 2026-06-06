output "ckpt_bucket"  { value = aws_s3_bucket.ckpts.bucket }
output "stats_url"   { value = aws_lambda_function_url.stats.function_url }
output "data_bucket" { value = aws_s3_bucket.ckpts.bucket }