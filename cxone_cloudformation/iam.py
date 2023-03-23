import aws_cdk.aws_iam as iam
from constructs import Construct
from .customized_parameters import (
    using_existing_vpc_flow_log_role,
    bucket_name_suffix,
    iam_name_suffix,
)


def get_minio_gateway_eks_node_group_iam_role(scope: Construct):
    res = "arn:aws:s3:::*" + bucket_name_suffix
    role = iam.Role(
        scope=scope,
        id="MinioGatewayEksNodeGroupRole",
        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        inline_policies={
            "s3_buckets_policy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=["s3:*"],
                        resources=[
                            res,
                            res + "/*"
                        ]
                    )
                ]
            )
        },
        role_name="-".join(["minio-gateway-eks-node-group", iam_name_suffix])
    )
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"))
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"))
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"))
    return role


def get_vpc_flow_log_role(scope: Construct):
    return iam.Role(
        scope=scope,
        id="VpcFlowLogRole",
        assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
        inline_policies={
            "vpc_logs_policy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "logs:PutLogEvents",
                            "logs:DescribeLogStreams",
                            "logs:DescribeLogGroups",
                            "logs:CreateLogStream",
                        ],
                        resources=["*"],
                        sid="AWSVPCFlowLogsPushToCloudWatch",
                    )
                ]
            )
        },
        role_name="-".join(["vpc-flow-log-role", iam_name_suffix])
    )


def get_load_balancer_controller_role(scope: Construct):
    return iam.Role(
        scope=scope,
        id="LoadBalancerControllerRole",
        assumed_by=iam.ServicePrincipal("elasticloadbalancing.amazonaws.com"),
        description="IRSA role for cluster load balancer controller",
        inline_policies={
            "load_balancer_policy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=["iam:CreateServiceLinkedRole"],
                        resources=["*"],
                        conditions={
                            "StringEquals": {
                                "iam:AWSServiceName": "elasticloadbalancing.amazonaws.com"
                            }
                        }
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "ec2:DescribeAccountAttributes",
                            "ec2:DescribeAddresses",
                            "ec2:DescribeAvailabilityZones",
                            "ec2:DescribeInternetGateways",
                            "ec2:DescribeVpcs",
                            "ec2:DescribeVpcPeeringConnections",
                            "ec2:DescribeSubnets",
                            "ec2:DescribeSecurityGroups",
                            "ec2:DescribeInstances",
                            "ec2:DescribeNetworkInterfaces",
                            "ec2:DescribeTags",
                            "ec2:GetCoipPoolUsage",
                            "ec2:DescribeCoipPools",
                            "elasticloadbalancing:DescribeLoadBalancers",
                            "elasticloadbalancing:DescribeLoadBalancerAttributes",
                            "elasticloadbalancing:DescribeListeners",
                            "elasticloadbalancing:DescribeListenerCertificates",
                            "elasticloadbalancing:DescribeSSLPolicies",
                            "elasticloadbalancing:DescribeRules",
                            "elasticloadbalancing:DescribeTargetGroups",
                            "elasticloadbalancing:DescribeTargetGroupAttributes",
                            "elasticloadbalancing:DescribeTargetHealth",
                            "elasticloadbalancing:DescribeTags",
                        ],
                        resources=["*"],
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "cognito-idp:DescribeUserPoolClient",
                            "acm:ListCertificates",
                            "acm:DescribeCertificate",
                            "iam:ListServerCertificates",
                            "iam:GetServerCertificate",
                            "waf-regional:GetWebACL",
                            "waf-regional:GetWebACLForResource",
                            "waf-regional:AssociateWebACL",
                            "waf-regional:DisassociateWebACL",
                            "wafv2:GetWebACL",
                            "wafv2:GetWebACLForResource",
                            "wafv2:AssociateWebACL",
                            "wafv2:DisassociateWebACL",
                            "shield:GetSubscriptionState",
                            "shield:DescribeProtection",
                            "shield:CreateProtection",
                            "shield:DeleteProtection"
                        ],
                        resources=["*"]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "ec2:AuthorizeSecurityGroupIngress",
                            "ec2:RevokeSecurityGroupIngress"
                        ],
                        resources=["*"]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "ec2:CreateSecurityGroup"
                        ],
                        resources=["*"]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "ec2:CreateTags"
                        ],
                        resources=["arn:aws:ec2:*:*:security-group/*"],
                        conditions={
                            "StringEquals": {
                                "ec2:CreateAction": "CreateSecurityGroup"
                            },
                            "Null": {
                                "aws:RequestTag/elbv2.k8s.aws/cluster": "false"
                            }
                        },
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "ec2:CreateTags",
                            "ec2:DeleteTags"
                        ],
                        resources=["arn:aws:ec2:*:*:security-group/*"],
                        conditions={
                            "Null": {
                                "aws:RequestTag/elbv2.k8s.aws/cluster": "true",
                                "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                            }
                        },
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "ec2:AuthorizeSecurityGroupIngress",
                            "ec2:RevokeSecurityGroupIngress",
                            "ec2:DeleteSecurityGroup"
                        ],
                        resources=["*"],
                        conditions={
                            "Null": {
                                "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                            }
                        },
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:CreateLoadBalancer",
                            "elasticloadbalancing:CreateTargetGroup"
                        ],
                        resources=["*"],
                        conditions={
                            "Null": {
                                "aws:RequestTag/elbv2.k8s.aws/cluster": "false"
                            }
                        },
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:CreateListener",
                            "elasticloadbalancing:DeleteListener",
                            "elasticloadbalancing:CreateRule",
                            "elasticloadbalancing:DeleteRule"
                        ],
                        resources=["*"]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:AddTags",
                            "elasticloadbalancing:RemoveTags"
                        ],
                        resources=[
                            "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*",
                            "arn:aws:elasticloadbalancing:*:*:loadbalancer/net/*/*",
                            "arn:aws:elasticloadbalancing:*:*:loadbalancer/app/*/*"
                        ],
                        conditions={
                            "Null": {
                                "aws:RequestTag/elbv2.k8s.aws/cluster": "true",
                                "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                            }
                        }
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:AddTags",
                            "elasticloadbalancing:RemoveTags"
                        ],
                        resources=[
                            "arn:aws:elasticloadbalancing:*:*:listener/net/*/*/*",
                            "arn:aws:elasticloadbalancing:*:*:listener/app/*/*/*",
                            "arn:aws:elasticloadbalancing:*:*:listener-rule/net/*/*/*",
                            "arn:aws:elasticloadbalancing:*:*:listener-rule/app/*/*/*"
                        ]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:ModifyLoadBalancerAttributes",
                            "elasticloadbalancing:SetIpAddressType",
                            "elasticloadbalancing:SetSecurityGroups",
                            "elasticloadbalancing:SetSubnets",
                            "elasticloadbalancing:DeleteLoadBalancer",
                            "elasticloadbalancing:ModifyTargetGroup",
                            "elasticloadbalancing:ModifyTargetGroupAttributes",
                            "elasticloadbalancing:DeleteTargetGroup"
                        ],
                        resources=["*"],
                        conditions={
                            "Null": {
                                "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                            }
                        },
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:RegisterTargets",
                            "elasticloadbalancing:DeregisterTargets"
                        ],
                        resources=[
                            "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*"
                        ]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "elasticloadbalancing:SetWebAcl",
                            "elasticloadbalancing:ModifyListener",
                            "elasticloadbalancing:AddListenerCertificates",
                            "elasticloadbalancing:RemoveListenerCertificates",
                            "elasticloadbalancing:ModifyRule"
                        ],
                        resources=["*"]
                    ),
                ]
            )
        },
        role_name="-".join(["load_balancer_controller", iam_name_suffix])
    )


def get_external_dns_role(scope: Construct):
    return iam.Role(
        scope=scope,
        id="ExternalDnsRole",
        assumed_by=iam.ServicePrincipal("route53.amazonaws.com"),
        description="IRSA role for cluster external dns controller",
        inline_policies={
            "external_dns_policy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "route53:ChangeResourceRecordSets"
                        ],
                        resources=[
                            "arn:aws:route53:::hostedzone/*"
                        ]
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "route53:ListHostedZones",
                            "route53:ListResourceRecordSets"
                        ],
                        resources=[
                            "*"
                        ]
                    ),
                ]
            )
        },
        role_name="-".join(["external-dns", iam_name_suffix])
    )


def get_cluster_autoscaler_role(scope: Construct):
    return iam.Role(
        scope=scope,
        id="ClusterAutoscalerRole",
        assumed_by=iam.ServicePrincipal("autoscaling.amazonaws.com"),
        description="IRSA role for cluster autoscaler",
        inline_policies={
            "cluster_autoscaler_policy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "autoscaling:DescribeAutoScalingGroups",
                            "autoscaling:DescribeAutoScalingInstances",
                            "autoscaling:DescribeLaunchConfigurations",
                            "autoscaling:SetDesiredCapacity",
                            "autoscaling:DescribeTags",
                            "autoscaling:TerminateInstanceInAutoScalingGroup",
                            "ec2:DescribeInstanceTypes"
                        ],
                        resources=[
                            "*"
                        ]
                    ),
                ]
            )
        },
        role_name="-".join(["cluster-autoscaler", iam_name_suffix])
    )


def get_aws_ebs_csi_driver_role(scope: Construct):
    role = iam.Role(
        scope=scope,
        id="aws_ebs_csi_driver_role",
        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        description="IRSA role for ebs csi driver role",
        role_name="-".join(["aws_ebs_csi_driver_role", iam_name_suffix])
    )
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEBSCSIDriverPolicy"))
    return role
