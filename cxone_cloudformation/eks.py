import os
import aws_cdk.aws_eks as eks
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_autoscaling as autoscaling
import aws_cdk.aws_s3_assets as assets
from constructs import Construct

from .customized_parameters import (
    deployment_id,
    region,
    external_security_group_name,
    internal_security_group_name,
    host_zone_id,
)

from aws_cdk import (
    RemovalPolicy,
    Duration,
)


def get_eks(scope: Construct, cluster_name, vpc, kms,
            load_balancer_controller_role,
            external_dns_role,
            cluster_autoscaler_role,
            aws_ebs_csi_driver_role):

    eks_cluster = eks.Cluster(
        scope=scope,
        id="EksCluster",
        default_capacity=0,
        default_capacity_instance=None,
        default_capacity_type=None,
        cluster_logging=[
            eks.ClusterLoggingTypes.AUDIT,
            eks.ClusterLoggingTypes.API,
            eks.ClusterLoggingTypes.AUTHENTICATOR,
            eks.ClusterLoggingTypes.SCHEDULER
        ],
        endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
        secrets_encryption_key=kms,
        service_ipv4_cidr="172.20.0.0/16",
        version=eks.KubernetesVersion.V1_21,
        cluster_name=cluster_name,
        output_cluster_name=True,
        output_config_command=True,
        vpc=vpc,
        vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)],
    )

    for node_group in ["ast_nodes", "sast_nodes", "sast_nodes_medium", "sast_nodes_large", "sast_nodes_extra_large",
                       "sast_nodes_xxl", "kics_nodes", "minio_gateway_nodes", "repostore_nodes", ]:
        eks_cluster.add_auto_scaling_group_capacity(
            id=node_group,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.XLARGE2),
            bootstrap_enabled=False,
            bootstrap_options=None,
            machine_image_type=eks.MachineImageType.AMAZON_LINUX_2,
            map_role=True,
            spot_interrupt_handler=True,
            allow_all_outbound=True,
            associate_public_ip_address=None,
            auto_scaling_group_name=None,
            block_devices=[autoscaling.BlockDevice(device_name="/dev/xvda", volume=autoscaling.BlockDeviceVolume.ebs(
                volume_size=50,
                encrypted=True,
                delete_on_termination=True,
                iops=3000,
                throughput=125,
                volume_type=autoscaling.EbsDeviceVolumeType.GP3
            ))],
            capacity_rebalance=None,
            cooldown=None,
            default_instance_warmup=None,
            desired_capacity=0 if node_group in ["sast_nodes_medium", "sast_nodes_large", "sast_nodes_extra_large",
                                                 "sast_nodes_xxl"] else 1,
            group_metrics=None,
            health_check=None,
            ignore_unmodified_size_properties=None,
            instance_monitoring=None,
            key_name=None,
            max_capacity=10,
            max_instance_lifetime=None,
            min_capacity=0 if node_group in ["sast_nodes_medium", "sast_nodes_large", "sast_nodes_extra_large",
                                             "sast_nodes_xxl"] else 1,
            new_instances_protected_from_scale_in=None,
            notifications=None,
            signals=None,
            spot_price=None,
            termination_policies=None,
            update_policy=None,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        eks_cluster.add_nodegroup_capacity(
            id=node_group,
            ami_type=eks.NodegroupAmiType.AL2_X86_64,
            capacity_type=eks.CapacityType.ON_DEMAND,
            desired_size=1,
            disk_size=50,
            force_update=True,
            instance_types=[ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.XLARGE2)],
            max_size=10,
            min_size=1,
            nodegroup_name=node_group,
            node_role=None,
            release_version=None,
            remote_access=None,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            tags=None,
            taints=None,
        )

    eks_cluster.add_service_account(
        id="aws-load-balancer-controller",
        annotations={
            "eks.amazonaws.com/role-arn": load_balancer_controller_role.role_arn
        },
        name="aws-load-balancer-controller",
        namespace="kube-system",
    )
    eks_cluster.add_service_account(
        id="external-dns",
        annotations={
            "eks.amazonaws.com/role-arn": external_dns_role.role_arn
        },
        name="external-dns",
        namespace="kube-system",
    )
    eks_cluster.add_service_account(
        id="cluster-autoscaler",
        annotations={
            "eks.amazonaws.com/role-arn": cluster_autoscaler_role.role_arn
        },
        name="cluster-autoscaler",
        namespace="kube-system",
    )
    eks_cluster.add_service_account(
        id="aws-ebs-csi-driver",
        annotations={
            "eks.amazonaws.com/role-arn": aws_ebs_csi_driver_role.role_arn
        },
        name="aws-ebs-csi-driver",
        namespace="kube-system",
    )

    parent_folder = os.path.dirname(os.path.realpath(__file__))
    assets_folder = os.path.join(parent_folder, "s3_assets")

    eks_cluster.add_helm_chart(
        id="aws-load-balancer-controller-helm-chart",
        chart=None,
        chart_asset=assets.Asset(
            scope=scope,
            id="aws-load-balancer-controller-helm-chart-asset",
            path=os.path.join(assets_folder, "aws-load-balancer-controller-1.4.5.zip")
        ),
        create_namespace=True,
        namespace="kube-system",
        values={
            "clusterName": deployment_id,
            "serviceAccount.create": "false",
            "serviceAccount.name": "aws-load-balancer-controller",
            "region": region,
        },
        version=None,
    )
    eks_cluster.add_helm_chart(
        id="external-dns-helm-chart",
        chart=None,
        chart_asset=assets.Asset(
            scope=scope,
            id="external-dns-helm-chart-asset",
            path=os.path.join(assets_folder, "external-dns-1.11.0.zip")
        ),
        create_namespace=True,
        namespace="kube-system",
        values={
            "txtOwnerId": host_zone_id,
            "serviceAccount.create": "false",
            "serviceAccount.name": "external-dns",
        },
        version=None,
    )
    eks_cluster.add_helm_chart(
        id="cluster-autoscaler-helm-chart",
        chart=None,
        chart_asset=assets.Asset(
            scope=scope,
            id="cluster-autoscaler-helm-chart-asset",
            path=os.path.join(assets_folder, "cluster-autoscaler-9.21.0.zip")
        ),
        create_namespace=True,
        namespace="kube-system",
        values={
            "image.tag": "v1.23.0",
            "awsRegion": region,
            "rbac.create": "true",
            "rbac.serviceAccount.create": "false",
            "rbac.serviceAccount.name": "cluster-autoscaler"
        },
        version=None,
    )
    eks_cluster.add_helm_chart(
        id="aws-ebs-csi-driver-helm-chart",
        chart=None,
        chart_asset=assets.Asset(
            scope=scope,
            id="aws-ebs-csi-driver-helm-chart-asset",
            path=os.path.join(assets_folder, "aws-ebs-csi-driver-2.13.0.zip")
        ),
        create_namespace=True,
        namespace="kube-system",
        values={
            "node.tolerateAllTaints": "true",
            "controller.serviceAccount.create": "false",
            "controller.serviceAccount.name": "aws-ebs-csi-driver",
            "node.serviceAccount.create": "false",
            "node.serviceAccount.name": "aws-ebs-csi-driver",
        },
        version=None,
    )
    coredns_addon = eks.CfnAddon(scope, "CoreDnsCfnAddon",
                                 addon_name="coredns",
                                 cluster_name=cluster_name,
                                 resolve_conflicts="OVERWRITE",
                                 )

    kube_proxy_addon = eks.CfnAddon(scope, "KubeProxyCfnAddon",
                                    addon_name="kube-proxy",
                                    cluster_name=cluster_name,
                                    resolve_conflicts="OVERWRITE",
                                    )

    vpc_cni_addon = eks.CfnAddon(scope, "VpcCniCfnAddon",
                                 addon_name="vpc-cni",
                                 cluster_name=cluster_name,
                                 resolve_conflicts="OVERWRITE",
                                 )
