from constructs import Construct
from aws_cdk.aws_ec2 import (
    SecurityGroup,
    Peer,
    Port,
)

from .customized_parameters import (
    deployment_id,
    external_security_group_name,
    internal_security_group_name,
)
from aws_cdk import (
    RemovalPolicy,
)


def get_security_groups(scope: Construct, vpc):

    external_security_group = SecurityGroup(
        scope=scope,
        id="external_security_group",
        vpc=vpc,
        allow_all_ipv6_outbound=True,
        allow_all_outbound=True,
        description=f"External Security group for AST deployment called {deployment_id}",
        disable_inline_rules=True,
        security_group_name=external_security_group_name
    )
    external_security_group.add_ingress_rule(
        peer=Peer.ipv4("0.0.0.0/0"),
        connection=Port.tcp(80),
        description="HTTP"
    )
    external_security_group.add_ingress_rule(
        peer=Peer.ipv4("0.0.0.0/0"),
        connection=Port.tcp(22),
        description="SSH"
    )
    external_security_group.add_ingress_rule(
        peer=Peer.ipv4("0.0.0.0/0"),
        connection=Port.tcp(443),
        description="HTTPS"
    )
    external_security_group.add_ingress_rule(
        peer=Peer.ipv4("0.0.0.0/0"),
        connection=Port.tcp(6443),
        description="Kubernetes API Server"
    )
    external_security_group.add_ingress_rule(
        peer=Peer.ipv4("0.0.0.0/0"),
        connection=Port.all_icmp(),
        description="All IPV4 ICMP"
    )
    external_security_group.apply_removal_policy(RemovalPolicy.DESTROY)

    internal_security_group = SecurityGroup(
        scope=scope,
        id="internal_security_group",
        vpc=vpc,
        allow_all_ipv6_outbound=True,
        allow_all_outbound=True,
        description=f"Internal Security group for AST deployment called {deployment_id}",
        disable_inline_rules=True,
        security_group_name=internal_security_group_name
    )
    internal_security_group.add_ingress_rule(
        peer=Peer.ipv4(vpc.vpc_cidr_block),
        connection=Port.all_traffic(),
        description="All protocols"
    )
    internal_security_group.apply_removal_policy(RemovalPolicy.DESTROY)
    return external_security_group, internal_security_group
