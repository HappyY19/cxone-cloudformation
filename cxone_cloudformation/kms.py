import aws_cdk.aws_kms as kms
from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    Duration,
)


def get_kms(scope: Construct, using_existing_one: bool = False, key_arn=None):
    """

    :param scope:
    :param using_existing_one:
    :param key_arn:
    :return: IKey
    """
    key = kms.Key(
        scope=scope,
        id="kms",
        enable_key_rotation=True,
        pending_window=Duration.days(7),
        removal_policy=RemovalPolicy.DESTROY
    )
    if using_existing_one:
        key = kms.Key.from_key_arn(key_arn=key_arn)

    return key
