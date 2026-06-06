data "archive_file" "producer" {
  type        = "zip"
  source_dir  = "${path.module}/../hep-trigger-ml/lambdas/producer"
  output_path = "${path.module}/build/producer.zip"
}
data "archive_file" "inference" {
  type        = "zip"
  source_dir  = "${path.module}/../hep-trigger-ml/lambdas/inference"
  output_path = "${path.module}/build/inference.zip"
}
data "archive_file" "stats" {
  type        = "zip"
  source_dir  = "${path.module}/../hep-trigger-ml/lambdas/stats"
  output_path = "${path.module}/build/stats.zip"
}

resource "aws_lambda_function" "producer" {
  function_name    = "hep-producer"
  runtime          = "python3.12"
  handler          = "handler.handler"
  filename         = data.archive_file.producer.output_path
  source_code_hash = data.archive_file.producer.output_base64sha256
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  environment {
    variables = {
      QUEUE_URL   = aws_sqs_queue.events.url
      DATA_BUCKET = aws_s3_bucket.ckpts.bucket
      BATCH       = "50"
    }
  }
}
resource "aws_lambda_function" "inference" {
  function_name    = "hep-inference"
  runtime          = "python3.12"
  handler          = "handler.handler"
  filename         = data.archive_file.inference.output_path
  source_code_hash = data.archive_file.inference.output_base64sha256
  role             = aws_iam_role.lambda.arn
  timeout          = 30
  memory_size      = 256
  environment {
    variables = {
      TABLE        = aws_dynamodb_table.stats.name
      MODEL_BUCKET = aws_s3_bucket.ckpts.bucket
    }
  }
}
resource "aws_lambda_function" "stats" {
  function_name    = "hep-stats"
  runtime          = "python3.12"
  handler          = "handler.handler"
  filename         = data.archive_file.stats.output_path
  source_code_hash = data.archive_file.stats.output_base64sha256
  role             = aws_iam_role.lambda.arn
  timeout          = 10
  environment {
    variables = {
      TABLE = aws_dynamodb_table.stats.name
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn = aws_sqs_queue.events.arn
  function_name    = aws_lambda_function.inference.arn
  batch_size       = 10
}
resource "aws_lambda_function_url" "stats" {
  function_name      = aws_lambda_function.stats.function_name
  authorization_type = "NONE"
}
resource "aws_cloudwatch_event_rule" "tick" {
  name                = "hep-tick"
  schedule_expression = "rate(5 minutes)"
}
resource "aws_cloudwatch_event_target" "tick" {
  rule = aws_cloudwatch_event_rule.tick.name
  arn  = aws_lambda_function.producer.arn
}
resource "aws_lambda_permission" "events" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.producer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.tick.arn
}