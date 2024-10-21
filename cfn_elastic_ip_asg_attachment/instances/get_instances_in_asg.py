from typing import List

import boto3

def get_instances_in_asg(session: boto3.Session, asg_name: str) -> List[str]:
    asg = session.client("autoscaling")
    instances = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name]
    )["AutoScalingGroups"][0]["Instances"]

    return [instance["InstanceId"] for instance in instances]
