import aws_cdk.aws_elasticache as elasticache
import aws_cdk.aws_ec2 as ec2

from aws_cdk import (
    RemovalPolicy,
)
from constructs import Construct
from .customized_parameters import (
    deployment_id,
    internal_security_group_name,
)


def get_redis_cluster(scope: Construct, vpc: ec2.Vpc, redis_security_group):
    isolated_subnets_ids = [ps.subnet_id for ps in vpc.isolated_subnets]
    redis_subnet_group = elasticache.CfnSubnetGroup(
        scope=scope,
        id="redis_subnet_group",
        subnet_ids=isolated_subnets_ids,
        description="subnet group for redis"
    )

    cfn_cache_cluster = elasticache.CfnCacheCluster(
        scope=scope,
        id="MyCfnCacheCluster",
        cache_node_type="cache.t4g.medium",
        engine="Redis",
        num_cache_nodes=1,
        cache_subnet_group_name=redis_subnet_group.ref,
        auto_minor_version_upgrade=False,
        cluster_name=deployment_id,
        engine_version="6.x",
        ip_discovery="ipv4",
        network_type="ipv4",
        port=6379,
        preferred_maintenance_window="sun:23:00-mon:01:30",
        transit_encryption_enabled=False,
        vpc_security_group_ids=[redis_security_group.security_group_id]
    )

    cfn_cache_cluster.apply_removal_policy(RemovalPolicy.DESTROY)
