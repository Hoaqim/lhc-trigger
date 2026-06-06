resource "aws_sqs_queue" "events" {
  name                       = "hep-events"
  visibility_timeout_seconds = 60
}
