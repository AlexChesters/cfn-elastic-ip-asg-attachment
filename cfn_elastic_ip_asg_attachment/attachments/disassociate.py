import boto3

def disassociate_address(session: boto3.Session, allocation_id: str):
    client = session.client("ec2")

    addresses = client.describe_addresses(
        AllocationIds=[allocation_id]
    )["Addresses"]

    association_id = addresses[0]["AssociationId"]

    client.disassociate_address(
        AssociationId=association_id,
        DryRun=True
    )
