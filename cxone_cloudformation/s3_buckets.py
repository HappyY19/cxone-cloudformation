import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_iam as iam
from .customized_parameters import (
    deployment_id,
    s3_retention_period,
    bucket_name_suffix,
)
from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    Duration,
)


def get_all_s3_buckets(scope: Construct):
    """

    :param scope:
    :return:
    """
    buckets = []
    bucket_names = [
        "apisec", "audit", "configuration", "engine-logs", "imports", "kics-metadata", "kics-worker", "logs",
        "misc", "queries", "redis-shared-bucket", "report-templates", "reports", "repostore", "sast-metadata",
        "sast-worker", "sca-worker", "scan-results-storage", "scans", "source-resolver", "uploads"
    ]

    for index, name in enumerate(bucket_names):
        bucket = s3.Bucket(
            scope=scope,
            id="-".join(["bucket", str(index)]),
            access_control=s3.BucketAccessControl.PRIVATE,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name="-".join([name, bucket_name_suffix]),
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=False,
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    id="Transition-To-Intelligent-Tiering",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                            transition_after=Duration.days(0)
                        ),
                    ]
                ),
                s3.LifecycleRule(
                    id="-".join([str(s3_retention_period), "Days-Non-Current-Expiration"]),
                    enabled=True,
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                    noncurrent_version_expiration=Duration.days(s3_retention_period),
                    expired_object_delete_marker=True,
                )
            ],
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            removal_policy=RemovalPolicy.DESTROY,
        )
        bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="denyInsecureTransport",
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()],
            actions=["s3:*"],
            resources=[bucket.bucket_arn, bucket.arn_for_objects('*')],
            conditions={
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        ))
        cdk.Tag(key="Name", value=f"{deployment_id} {name} bucket").visit(bucket)
        cdk.Tag(key="Environment", value=f"{deployment_id}").visit(bucket)
        buckets.append(bucket)
    return buckets
