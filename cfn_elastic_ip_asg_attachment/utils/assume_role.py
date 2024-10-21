import boto3

session = boto3.Session()

def assume_role(role_arn: str) -> boto3.Session:
    sts_client = session.client("sts")
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="CfnElasticIpAsgAttachment"
    )
    credentials = assumed_role["Credentials"]

    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"]
    )
