resource "aws_msk_cluster" "events" {
  cluster_name = "hep-events"
  kafka_version = "3.6.0"
  number_of_broker_nodes = 2
  broker_node_group_info {
    instance_type = "kafka.t3.small"
    client_subnets = module.vps.private_subnets
    security_groups = [aws_security_group.msk.id]
  }
}