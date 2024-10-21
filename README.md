# cfn-elastic-ip-asg-attachment
CloudFormation custom resource that allows you to attach Elastic IPs to EC2 Instances in an AutoScaling Group

# Deployment
1. `make package`
1. `aws cloudformation package --template-file ./stacks/lambda.yml --s3-bucket <S3_BUCKET_FOR_CLOUDFORMATION_ARTIFACTS> --s3-prefix artifacts/cfn-elastic-ip-asg-attachment --output-template-file ./stacks/lambda.yml`
1. Deploy the packaged [`lambda.yml`](./stacks/lambda.yml) CloudFormation template to your AWS account
    - this template takes an optional parameter, `OrgId`, which, if set to an AWS Organisation ID will
    allow any principal in that organisation to invoke the function

# Usage
Below is a CloudFormation template containing the bare minimum needed to use this custom resource
```yaml
Parameters:
  AMI:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64
  EIPASGLambdaAccount:
    Type: String
  VPCId:
    Type: String
  Subnets:
    Type: CommaDelimitedList
Resources:
  EIPASGAttachment:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      ServiceToken: !Sub "arn:${AWS::Partition}:lambda:${AWS::Region}:${EIPASGLambdaAccount}:function:live-cfn-elastic-ip-asg-attachment"
      ServiceTimeout: 300
      AttachmentRole: !GetAtt EIPASGAttachmentRole.Arn
      AllocationIds: !Join
        - ","
        - - !GetAtt ElasticIp1.AllocationId
          - !GetAtt ElasticIp2.AllocationId
          - !GetAtt ElasticIp3.AllocationId
      AutoScalingGroupName: !Ref AutoScalingGroup
  ElasticIp1:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc
  ElasticIp2:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc
  ElasticIp3:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - ec2.amazonaws.com
            Action:
              - sts:AssumeRole
  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Path: /
      Roles:
      - !Ref EC2Role
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Access to the EC2
      SecurityGroupEgress:
        - CidrIp: 0.0.0.0/0
          IpProtocol: "-1"
        - CidrIpv6: ::/0
          IpProtocol: "-1"
      SecurityGroupIngress:
        - CidrIp: 0.0.0.0/0
          FromPort: 80
          ToPort: 80
          IpProtocol: tcp
        - CidrIp: 0.0.0.0/0
          FromPort: 443
          ToPort: 443
          IpProtocol: tcp
      VpcId: !Ref VPCId
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        ImageId: !Ref AMI
        InstanceType: t4g.nano
        IamInstanceProfile:
          Name: !Ref EC2InstanceProfile
        SecurityGroupIds:
          - !Ref SecurityGroup
        MetadataOptions:
          HttpEndpoint: enabled
          HttpTokens: required
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      VPCZoneIdentifier:
        - !Select [0, !Ref Subnets]
        - !Select [1, !Ref Subnets]
        - !Select [2, !Ref Subnets]
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 0
      MaxSize: 3
      DesiredCapacity: 3
  EIPASGAttachmentRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:${AWS::Partition}:iam::${EIPASGLambdaAccount}:role/live-cfn-elastic-ip-asg-attachment"
            Action:
              - sts:AssumeRole
      Policies:
        - PolicyName: eip-asg-attachment-policy
          PolicyDocument:
            Statement:
              - Effect: Allow
                Action:
                  - ec2:AssociateAddress
                Resource:
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/${ElasticIp1.AllocationId}"
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/${ElasticIp2.AllocationId}"
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/${ElasticIp3.AllocationId}"
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:instance/*"
              - Effect: Allow
                Action:
                  - ec2:DisassociateAddress
                Resource:
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/${ElasticIp1.AllocationId}"
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/${ElasticIp2.AllocationId}"
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/${ElasticIp3.AllocationId}"
                  - !Sub "arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:network-interface/*"
              - Effect: Allow
                Action:
                  - ec2:DescribeAddresses
                Resource:
                  - "*"
              - Effect: Allow
                Action:
                  - autoscaling:DescribeAutoScalingGroups
                Resource:
                  - "*"
```

# Things to be aware of
- The number of EC2 instances in the AutoScaling Group must match the number of `AllocationIds` provided to the
custom resource
