import aws_cdk.aws_ec2 as ec2
from constructs import Construct
from .customized_parameters import (
    deployment_id,
    using_existing_vpc,
    region,
    vpc_id,
    availability_zones,
    vpc_cidr,
    public_subnet_cidr_mask,
    private_subnet_cidr_mask,
    isolated_subnet_cidr_mask,

)
from aws_cdk import (
    RemovalPolicy,
)


def get_vpc(scope: Construct):
    vpc = ec2.Vpc(
        scope=scope,
        id="VPC",
        availability_zones=availability_zones,
        enable_dns_hostnames=True,
        enable_dns_support=True,
        flow_logs={
            "FlowLogCloudwatch": ec2.FlowLogOptions(
                destination=ec2.FlowLogDestination.to_cloud_watch_logs(),
            )
        },
        gateway_endpoints={"S3": ec2.GatewayVpcEndpointOptions(service=ec2.GatewayVpcEndpointAwsService.S3)},
        ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
        nat_gateway_provider=ec2.NatProvider.gateway(),
        nat_gateways=1,
        nat_gateway_subnets=ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PUBLIC
        ),
        subnet_configuration=[
            ec2.SubnetConfiguration(
                cidr_mask=public_subnet_cidr_mask,
                name="-".join([deployment_id, "public", availability_zones[0]]),
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            ec2.SubnetConfiguration(
                cidr_mask=public_subnet_cidr_mask,
                name="-".join([deployment_id, "public", availability_zones[1]]),
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            ec2.SubnetConfiguration(
                cidr_mask=private_subnet_cidr_mask,
                name="-".join([deployment_id, "private", availability_zones[0]]),
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            ec2.SubnetConfiguration(
                cidr_mask=private_subnet_cidr_mask,
                name="-".join([deployment_id, "private", availability_zones[1]]),
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            ec2.SubnetConfiguration(
                cidr_mask=isolated_subnet_cidr_mask,
                name="-".join([deployment_id, "db", availability_zones[0]]),
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            ec2.SubnetConfiguration(
                cidr_mask=isolated_subnet_cidr_mask,
                name="-".join([deployment_id, "db", availability_zones[1]]),
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
        ],
        vpc_name=deployment_id,
    )
    vpc.apply_removal_policy(policy=RemovalPolicy.DESTROY)

    if using_existing_vpc:
        vpc = ec2.Vpc.from_lookup(
            scope=scope,
            id="VPC",
            region=region,
            vpc_id=vpc_id
        )
    return vpc

