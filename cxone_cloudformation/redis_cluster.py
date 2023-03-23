import aws_cdk.aws_elasticache as elasticache

from aws_cdk import (
    RemovalPolicy,
)
from constructs import Construct
from .customized_parameters import (
    deployment_id,
    internal_security_group_name,
)


def get_redis_cluster(scope: Construct):

    cfn_cache_cluster = elasticache.CfnCacheCluster(
        scope=scope,
        id="MyCfnCacheCluster",
        cache_node_type="cache.t4g.medium",
        engine="Redis",
        num_cache_nodes=1,
        auto_minor_version_upgrade=False,
        cache_security_group_names=[internal_security_group_name],
        cluster_name=deployment_id,
        engine_version="6.x",
        ip_discovery="ipv4",
        network_type="ipv4",
        port=6379,
        preferred_maintenance_window="sun:23:00-mon:01:30",
        transit_encryption_enabled=False,
    )

    cfn_cache_cluster.apply_removal_policy(RemovalPolicy.DESTROY)
