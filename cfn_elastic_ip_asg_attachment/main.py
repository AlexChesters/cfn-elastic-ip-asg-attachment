from aws_lambda_powertools import Logger
from crhelper import CfnResource
import boto3

from cfn_elastic_ip_asg_attachment.utils.validate_properties import validate_properties
from cfn_elastic_ip_asg_attachment.utils.assume_role import assume_role
from cfn_elastic_ip_asg_attachment.instances.get_instances_in_asg import get_instances_in_asg
from cfn_elastic_ip_asg_attachment.attachments.associate import associate_address
from cfn_elastic_ip_asg_attachment.attachments.disassociate import disassociate_address

logger = Logger()
cfn_helper = CfnResource()

def process_event(properties: dict, session: boto3.Session):
    instances = get_instances_in_asg(session, properties["AutoScalingGroupName"])

    if len(instances) != len(properties["AllocationIds"]):
        raise ValueError("Number of instances in ASG must match number of AllocationIds")

    return zip(properties["AllocationIds"], instances)

@cfn_helper.create
def create(event, _context):
    logger.append_keys(event="create")

    properties = validate_properties(event["ResourceProperties"])
    session = assume_role(properties["AttachmentRole"])

    for allocation_id, instance_id in process_event(properties, session):
        associate_address(session, allocation_id, instance_id)

@cfn_helper.update
def update(event, _context):
    logger.append_keys(event="update")

    properties = validate_properties(event["ResourceProperties"])
    session = assume_role(properties["AttachmentRole"])

    for allocation_id, instance_id in process_event(properties, session):
        disassociate_address(session, allocation_id)
        associate_address(session, allocation_id, instance_id)

@cfn_helper.delete
def delete(event, _context):
    logger.append_keys(event="delete")

    properties = validate_properties(event["ResourceProperties"])
    session = assume_role(properties["AttachmentRole"])

    for allocation_id, instance_id in process_event(properties, session):
        disassociate_address(session, allocation_id)

@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    cfn_helper(event, context)
