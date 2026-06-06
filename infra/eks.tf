module "eks" {
    source          = "terraform-aws-modules/eks/aws"
    cluster_name    = "hep-trigger"
    cluster_version = "1.30"
    vpc_id          = module.vpc.vpc_id
    subnet_ids      = module.vpc.private_subnets
    enable_irsa     = true
    eks_managed_node_groups = {
        services = { instance_types = ["t3.large"], min_size = 1, max_size = 3, desired_size = 2}
        training_spot = {
            instance_types = ["c5.xlarge", "c5a.xlarge"]
            capacity_type = "SPOT"
            min_size = 0, max_size = 4, desired_size = 1
            labels = { workload = "training" }
            taints = [{ key = "spot", value="true", effect = "NO_SCHEDULE"}]
        }
    }
}