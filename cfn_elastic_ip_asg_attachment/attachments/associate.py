import boto3

def associate_address(session: boto3.Session, allocation_id: str, instance_id: str) -> str:
    client = session.client("ec2")

    response = client.associate_address(
        AllocationId=allocation_id,
        InstanceId=instance_id
    )

    return response["AssociationId"]
