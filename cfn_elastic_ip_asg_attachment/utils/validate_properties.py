def validate_properties(properties: dict):
    # verify presence of required properties
    required_properties = ["AutoScalingGroupName", "AllocationIds", "AttachmentRole"]
    for prop in required_properties:
        if prop not in properties:
            raise ValueError(f"Missing required property: {prop}")

    # verify properties are not empty
    if not properties["AutoScalingGroupName"]:
        raise ValueError("AutoScalingGroupName must not be empty")
    if not properties["AllocationIds"]:
        raise ValueError("AllocationIds must not be empty")
    if not properties["AttachmentRole"]:
        raise ValueError("AttachmentRole must not be empty")

    return {
        "AutoScalingGroupName": properties["AutoScalingGroupName"],
        "AllocationIds": properties["AllocationIds"].split(","),
        "AttachmentRole": properties["AttachmentRole"]
    }
