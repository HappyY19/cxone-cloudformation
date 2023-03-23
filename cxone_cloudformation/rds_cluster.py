import aws_cdk.aws_rds as rds
import aws_cdk.aws_ec2 as ec2

from aws_cdk import (
    SecretValue,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
from .customized_parameters import (
    deployment_id,
    internal_security_group_name,
)


def get_rds_cluster(scope: Construct, vpc, kms, database_username: str, database_password: str, database_name: str,
                    database_security_group):

    return rds.DatabaseCluster(
        scope=scope,
        id="Database",
        engine=rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_13_4
        ),
        instance_props=rds.InstanceProps(
            vpc=vpc,
            auto_minor_version_upgrade=True,
            delete_automated_backups=True,
            enable_performance_insights=True,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.XLARGE),
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                scope=scope,
                id="ParameterGroup",
                parameter_group_name="default.aurora-postgresql13"
            ),
            performance_insight_encryption_key=kms,
            publicly_accessible=False,
            security_groups=[database_security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
            )
        ),
        backup=rds.BackupProps(
            retention=Duration.days(7),
            preferred_window="02:00-03:00"
        ),
        copy_tags_to_snapshot=False,
        cluster_identifier=deployment_id,
        credentials=rds.Credentials.from_password(
            username=database_username,
            password=SecretValue.unsafe_plain_text(database_password)
        ),
        default_database_name=database_name,
        deletion_protection=False,
        iam_authentication=False,
        instances=1,
        parameter_group=rds.ParameterGroup.from_parameter_group_name(
            scope=scope,
            id="CxOneDatabaseParameterGroup",
            parameter_group_name="default.aurora-postgresql13"
        ),
        removal_policy=RemovalPolicy.DESTROY,
        storage_encryption_key=kms,
        subnet_group=rds.SubnetGroup(
            scope=scope,
            id="RdsSubnetGroup",
            vpc=vpc,
            description=f"Database subnet group for {deployment_id}",
            # the properties below are optional
            removal_policy=RemovalPolicy.DESTROY,
            subnet_group_name=deployment_id,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )
    )
