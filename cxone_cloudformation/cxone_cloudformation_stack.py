from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from .s3_buckets import get_all_s3_buckets
from .vpc import get_vpc
from .security_groups import get_security_groups
from .redis_cluster import get_redis_cluster
from .kms import get_kms
from .rds_cluster import get_rds_cluster
from .customized_parameters import (
    database_username,
    database_password,
    database_name,
    deployment_id,
)
from .iam import (
    get_minio_gateway_eks_node_group_iam_role,
    get_vpc_flow_log_role,
    get_load_balancer_controller_role,
    get_external_dns_role,
    get_cluster_autoscaler_role,
    get_aws_ebs_csi_driver_role,
)
from .eks import get_eks


class CxOneCloudformationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CxoneCloudformationQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        kms = get_kms(scope=self)
        s3_buckets = get_all_s3_buckets(scope=self)
        vpc = get_vpc(scope=self)
        external_security_group, internal_security_group = get_security_groups(scope=self, vpc=vpc)
        redis_cluster = get_redis_cluster(scope=self)
        rds_cluster = get_rds_cluster(
            scope=self,
            vpc=vpc,
            kms=kms,
            database_name=database_name,
            database_username=database_username,
            database_password=database_password,
            database_security_group=internal_security_group
        )

        get_minio_gateway_eks_node_group_iam_role(scope=self)
        get_vpc_flow_log_role(scope=self)

        load_balancer_controller_role = get_load_balancer_controller_role(scope=self)
        external_dns_role = get_external_dns_role(scope=self)
        cluster_autoscaler_role = get_cluster_autoscaler_role(scope=self)
        aws_ebs_csi_driver_role = get_aws_ebs_csi_driver_role(scope=self)

        cluster_name = f"{deployment_id}"

        eks = get_eks(
            scope=self, cluster_name=cluster_name, vpc=vpc, kms=kms,
            load_balancer_controller_role=load_balancer_controller_role,
            external_dns_role=external_dns_role,
            cluster_autoscaler_role=cluster_autoscaler_role,
            aws_ebs_csi_driver_role=aws_ebs_csi_driver_role
        )

