import boto3
import os
from aws_assume_role_lib import assume_role


def get_bot3_session():
    region_name = os.environ.get("AWS_REGION", "us-east-2")
    if "AWS_ACCESS_KEY_ID" in os.environ and "AWS_SECRET_ACCESS_KEY" in os.environ:
        base_session = boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=region_name,
        )
    elif "AWS_PROFILE_NAME" in os.environ:
        base_session = boto3.Session(
            profile_name=os.environ["AWS_PROFILE_NAME"],
            region_name=region_name,
        )
    else:
        base_session = boto3.Session(region_name=region_name)

    if "AWS_ROLE_ARN" not in os.environ:
        return base_session

    return assume_role(base_session, os.environ["AWS_ROLE_ARN"])
