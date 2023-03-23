"""
customized parameters
"""
import string
import random
import datetime

# please use lower case letter and hyphen between words for deployment_id
deployment_id = "cx-one-apac"
s3_retention_period = 90

"""
VPC parameters
"""
# create new VPC
region = "ap-southeast-1"
availability_zones = ["ap-southeast-1a", "ap-southeast-1b"]
vpc_cidr = "10.0.0.0/16"
public_subnet_cidr_mask = 24
private_subnet_cidr_mask = 24
isolated_subnet_cidr_mask = 24

# use existing VPC
using_existing_vpc = False
vpc_id = ""

# flow log role
using_existing_vpc_flow_log_role = False


def get_random_string(length=6):
    inner_string = None

    def create_random_string_of_length():
        nonlocal inner_string
        if inner_string is None:
            inner_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return inner_string
    return create_random_string_of_length


random_string = get_random_string()
bucket_name_suffix = "-".join([deployment_id, random_string()])
iam_name_suffix = "-".join([deployment_id, datetime.datetime.today().strftime("%Y%m%d")])


"""
security groups parameters
"""
external_security_group_name = f"external-{deployment_id}-sg"
internal_security_group_name = f"internal-{deployment_id}-sg"

"""
RDS
"""
database_username = "cxone"
database_password = "dfs23S.SFif.238)sdf.23*-sf,dsfi8230z"
database_name = "cxonepostgres"

"""
EKS
"""
host_zone_id = ""
