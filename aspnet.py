from troposphere import Base64, Output, Join, FindInMap, GetAtt, Select, GetAZs, Equals, If, Parameter, Ref, Template, autoscaling, cloudformation, Tags
import troposphere.ec2 as ec2
from troposphere.ec2 import VPC, NetworkInterfaceProperty, SubnetRouteTableAssociation, EIP, Instance, Subnet, InternetGateway, VPCGatewayAttachment, Route, RouteTable, NetworkAcl, SecurityGroup, SecurityGroupRule
from troposphere.elasticloadbalancing import LoadBalancer
import troposphere.elasticloadbalancing as elb
from troposphere.policies import UpdatePolicy, AutoScalingRollingUpdate
from troposphere.autoscaling import AutoScalingGroup, Tag, LaunchConfiguration
from troposphere.cloudfront import Distribution,GeoRestriction,Restrictions ,DistributionConfig, ForwardedValues, Origin, DefaultCacheBehavior, CustomOrigin, ViewerCertificate, CacheBehavior
from troposphere.elasticache import CacheCluster, SubnetGroup
from troposphere.route53 import RecordSetType, AliasTarget
from troposphere.cloudformation import InitFile, InitFiles
from troposphere.iam import Role, InstanceProfile, PolicyType
from troposphere.sns import Subscription, Topic
from troposphere.s3 import Bucket, PublicRead, WebsiteConfiguration
import json, sys
from troposphere.cloudwatch import Alarm, MetricDimension
from os.path import expanduser

home = expanduser("~")

filename = home + "/outputs/aspnet.template"

t = Template()

try:
    metadata = json.loads(open('../metadata.json').read())
except IOError:
    metadata = json.loads(open('metadata.json').read())

t.add_description(
    "RB %s DotNet AWS Cloudformation Template" %metadata['service_name'].title()
)

t.add_mapping(
    'AWSRegion2AMI', {
        "us-east-1"      : { "AMI" : "ami-ac3a1cc4" },
        "us-west-2"      : { "AMI" : "ami-7f634e4f" },
        "us-west-1"      : { "AMI" : "ami-f544a3b1" }
    })
t.add_mapping(
    "EnvValues", {
        "prod"    :   {"cidr":"0"},
        "qa"      :   {"cidr":"1"},
        "dev"     :   {"cidr":"2"}
    }
)

ref_region = Ref('AWS::Region')
ref_stack_id = Ref('AWS::StackId')
ref_stack_name = Ref('AWS::StackName')
no_value = Ref("AWS::NoValue")
ref_account = {"Ref": "AWS::AccountId"}


vpc = t.add_parameter(Parameter(
    "VPC",
    Type="String",
    Description="VPC ID From Parent"
))
service_id = t.add_parameter(Parameter(
    "ServiceID",
    Type="String",
    Description="Service ID"
))
env = t.add_parameter(Parameter(
    "Environment",
    Type="String",
    Description="The environment being deployed into"
))
sglocal = t.add_parameter(Parameter(
    "sgLocal",
    Type="String",
    Description="VPC Access"
))
service = t.add_parameter(Parameter(
    "Service",
    Type="String",
    Description="Service Name",
))
subnet0 = t.add_parameter(Parameter(
    "Subnet0",
    Type="String",
    Description="Subnet0"
))
subnet1 = t.add_parameter(Parameter(
    "Subnet1",
    Type="String",
    Description="Subnet1"
))
port = t.add_parameter(Parameter(
    "Port",
    Type="String",
    Description="Port",
    Default = "80"
))
# The section below will be replaced from network template's outputs

KeyName = t.add_parameter(Parameter(
    "KeyName",
    Description="Key Pair Name (for use outside of Prod)",
    Type="String"
))
buildbucket = t.add_parameter(Parameter(
    "BuildBucket",
    Description="S3 Build Bucket",
    Type="String"
))
########################
#sslcertarn = t.add_parameter(Parameter(
#    "SslCertArn",
#    Type="String",
#    Description="ARN of SSL certificate",
#))
#sslcertid = t.add_parameter(Parameter(
#    "SslCertID",
#    Type="String",
#    Description="ID of SSL certificate",
#))

ScaleCapacity = t.add_parameter(Parameter(
    "ScaleCapacity",
    Default="1",
    Type="String",
    Description="Number of instances to initialize",
))
instance_type = t.add_parameter(Parameter(
    "InstanceType",
    Description="EC2 Instance Size",
    Type="String",
    Default="t2.small",
    AllowedValues=[
        "t2.micro", "t2.small", "m3.medium"
    ],
))
nat = t.add_parameter(Parameter(
    "NAT",
    Type="String",
    Description="Public NAT Instance"
))
VPCAvailabilityZone0 = t.add_parameter(Parameter(
    "VPCAvailabilityZone0",
    MinLength="1",
    Type="String",
    Description="First availability zone",
    MaxLength="255"
))

VPCAvailabilityZone1 = t.add_parameter(Parameter(
    "VPCAvailabilityZone1",
    MinLength="1",
    Type="String",
    Description="Second availability zone",
    MaxLength="255"
))
vpcenvcidr=10
## Resources
servicerole = t.add_resource(Role(
    "ServiceRole",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": [
                  "ec2.amazonaws.com"
                ]
              },
              "Action": [
                "sts:AssumeRole"
              ]
            }
          ]
        },
        Path =
          Join("", ['/',
              Ref(service),
              "/",
              Ref(env),'/'
          ])

))

serviceinstanceprofile = t.add_resource(InstanceProfile(
    "ServiceInstanceProfile",
    Path = Join("", ['/', Ref(service),"/",Ref(env),'/']),
    Roles=[Ref(servicerole)]
))

s3codedeployagent = t.add_resource(PolicyType(
    "S3CodeDeployAgentAccess",
        PolicyName="S3CodeDeployAgentAccess",
            PolicyDocument={
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": [
        { "Fn::Join":["",["arn:aws:s3:::", Ref(buildbucket)]]},
        "arn:aws:s3:::rb-code-builds/*",
        "arn:aws:s3:::aws-codedeploy-us-west-2/*",
        "arn:aws:s3:::aws-codedeploy-us-east-1/*"
      ]
    }
  ]
},
        Roles=[Ref(servicerole)]
    )
)

s3buildbucketiam = t.add_resource(PolicyType(
    "S3BuildBucketAccess",
        PolicyName="S3BuildBucketAccess",
            PolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                       {
              "Effect": "Allow",
              "Action": [
                "s3:ListBucket"
              ],
              "Condition": {
                "StringLike": {
                  "s3:prefix":  Ref(service)
                }
              },
              "Resource": [
                 { "Fn::Join":["",["arn:aws:s3:::", Ref(buildbucket)]]}
              ]
            },
            {
              "Effect": "Allow",
              "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:PutObject"
              ],
              "Resource": [
                { "Fn::Join": ["",["arn:aws:s3:::", Ref(buildbucket), "/", Ref(service), "/*"]]}
              ]
            }
                      ]
                                },
        Roles=[Ref(servicerole)]
    )
)
iaminfo = t.add_resource(PolicyType(
    "iamInfo",
        PolicyName="iamInfo",
            PolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {
                          "Effect": "Allow",
                          "Action": [ "ec2:DescribeTags"],
                          "Resource": ["*"]
                        },
                    {
                          "Effect": "Allow",
                          "Action": [ "ec2:DescribeInstances"],
                          "Resource": ["*"]
                        },
                    {
                          "Effect":"Allow",
                          "Action":"elasticache:DescribeCacheClusters",
                          "Resource":"*"
                          },
                    {
                          "Effect":"Allow",
                          "Action":"cloudformation:DescribeStackResource",
                          "Resource":Join("",['arn:aws:cloudformation:',ref_region,':',ref_account,':',ref_stack_name])
                          }
                      ]
                                },
        Roles=[Ref(servicerole)]
    )
)

lc = t.add_resource(LaunchConfiguration(
    "ServiceLaunchConfiguration",
    Metadata=autoscaling.Metadata(
        cloudformation.Init(
            cloudformation.InitConfigSets(
              default=['config', 'codedeploy', 'setupIIS']
            ),
                config= cloudformation.InitConfig(
                    packages = {
                        'msi': {'awscli' : 'https://s3.amazonaws.com/aws-cli/AWSCLI64.msi'}
                    },
            ),
        codedeploy=cloudformation.InitConfig(
                commands={
                "0DownloadCodeDeploy": {
                    "command": "PowerShell Read-S3Object -BucketName aws-codedeploy-us-west-2/latest -Key codedeploy-agent.msi -File c:\\tmp\\codedeploy-agent.msi"
                },
                "1InstallCodeDeploy" : {
                    "command" : "MsiExec.exe /i c:\\tmp\\codedeploy-agent.msi /log c:\\tmp\\codedeploy_install.log /quiet"
                }
            }
        ),
        setupIIS=cloudformation.InitConfig(
            commands={
                "0SetExecutionPolicy": {
                    "command": "PowerShell Set-ExecutionPolicy unrestricted -force"
                },
                "0ImportModule": {
                    "command": "PowerShell Import-Module ServerManager"
                },
                "0AddIISFeature": {
                    "command": "PowerShell Add-WindowsFeature Web-Static-Content,Web-Default-Doc,Web-Http-Errors,Web-Asp-Net,Web-Asp-Net45,Web-Net-Ext"
                },
                "1AddIISFeature": {
                    "command": "PowerShell Add-WindowsFeature Web-ISAPI-Ext,Web-ISAPI-Filter,Web-Http-Logging,Web-Log-Libraries,Web-Request-Monitor,Web-Http-Tracing"
                },
                "2AddIISFeature": {
                    "command": "PowerShell Add-WindowsFeature Web-Windows-Auth,Web-Filtering,Web-IP-Security,Web-Stat-Compression,Web-Dyn-Compression,Web-Mgmt-Console"
                },
                "3AddIISFeature": {
                    "command": "PowerShell Add-WindowsFeature Web-Scripting-Tools,Web-Metabase,Web-WMI,Web-Lgcy-Scripting,NET-Framework-Core"
                },
                "0AppPoolPerm": {
                    "command": "ICACLS C:\\InetPub\\wwwroot\\ /grant \"IIS AppPool\\DefaultAppPool:F\""
                }

            }

        ),
    )
),

    UserData=Base64(Join('', [
      "<powershell>\n",
              "cfn-init.exe -v",
              " --resource 'ServiceLaunchConfiguration'",
              "  -c 'default'"
              " --stack ", ref_stack_name,
              " --region ", ref_region, "\n",
              "cfn-signal.exe -e %ERRORCODE%",
              " --resource ServiceASG",
              " --stack ", ref_stack_name,
              " --region ", ref_region, "\n",

      "</powershell>\n",

      ])),

    ImageId=FindInMap("AWSRegion2AMI",ref_region,"AMI"),
    KeyName=Ref(KeyName),
    IamInstanceProfile=Ref(serviceinstanceprofile),
    InstanceType = "t2.small",
    SecurityGroups=[Ref(sglocal)],
))
elb = t.add_resource(LoadBalancer(
    "ServiceLoadBalancer",
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=120,
    ),
    Subnets=[Ref(subnet0), Ref(subnet1)],
    HealthCheck=elb.HealthCheck(
        Target=Join("",["TCP:80"]),
        HealthyThreshold="2",
        UnhealthyThreshold="2",
        Interval="10",
        Timeout="5",
    ),
    Listeners=[
        #elb.Listener(
        #    LoadBalancerPort="443",
        #    InstancePort="80",
        #    Protocol="HTTPS",
        #    InstanceProtocol="HTTP",
            #SSLCertificateId=Ref(sslcertarn)
        #),
        elb.Listener(
            LoadBalancerPort="80",
            InstancePort="80",
            Protocol="HTTP",
            InstanceProtocol="HTTP"
        )
    ],
    CrossZone=True,
    SecurityGroups=[Ref(sglocal)],
    Scheme = 'internal'
))
AutoscalingGroup = t.add_resource(AutoScalingGroup(
    "ServiceASG",
    DesiredCapacity=Ref(ScaleCapacity),
    Tags=[
        Tag("Environment", Ref(env), True),
        Tag("Service", Ref(service), True),
        Tag("Name", Join("", [Ref(service), '-', Ref(env)]), True)
    ],
    LaunchConfigurationName=Ref(lc),
    MinSize=Ref(ScaleCapacity),
    MaxSize=15,
    #AvailabilityZones=[GetAtt(subnet0,"AvailabilityZone"),GetAtt(subnet1,"AvailabilityZone")],
    AvailabilityZones=[Ref(VPCAvailabilityZone0), Ref(VPCAvailabilityZone1)],
    VPCZoneIdentifier=[Ref(subnet0), Ref(subnet1)],
    LoadBalancerNames=[Ref(elb)],
    HealthCheckType="EC2",
    HealthCheckGracePeriod=300,
    UpdatePolicy=UpdatePolicy(
        AutoScalingRollingUpdate=AutoScalingRollingUpdate(
            PauseTime='PT5M',
            MinInstancesInService="1",
            MaxBatchSize="1",
            WaitOnResourceSignals=True
        )
    )
))

healthyhostalarm = t.add_resource(
    Alarm(
        "NoHealthyHostAlarm",
        AlarmDescription=Ref(service),
        Namespace="ELB",
        MetricName="HealthyHostCount",
        Dimensions=[
            MetricDimension(
                Name=Ref(elb),
                Value=GetAtt("ServiceLoadBalancer", "DNSName")
            ),
        ],
        Statistic="Minimum",
        Period="60",
        EvaluationPeriods="1",
        Threshold="1",
        ComparisonOperator="LessThanThreshold"
    )
)

t.add_output([
    Output("ServiceELB", Value=GetAtt(elb, 'DNSName'))
])

template = (t.to_json())


if __name__ == "__main__":
    print template
    file = open('./%s.template' %service, 'w+')
    #file = open(filename, 'w+')
    file.write(template)
    file.close()
