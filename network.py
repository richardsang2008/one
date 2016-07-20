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
from os.path import expanduser

home = expanduser("~")

filename = home + "/outputs/network.template"

t = Template()

t.add_description(
    "Network Stack",
)
t.add_mapping(
    'AWSRegion2AMI', {
        "us-east-1"      : { "AMI" : "ami-b66ed3de" },
        "us-west-2"      : { "AMI" : "ami-b5a7ea85" }
    })
t.add_mapping(
     "AWSInstanceType2Arch", {
      "t2.micro"    : { "Arch" : "64" },
      "t2.medium"   : { "Arch" : "64" },
      "m3.medium"   : { "Arch" : "64" },
      "m3.large"    : { "Arch" : "64" },
      "m3.xlarge"   : { "Arch" : "64" }
    }
)
t.add_mapping(
    "EnvValues", {
        "prod"    :   {"cidr":"0"},
        "qa"      :   {"cidr":"1"},
        "dev"     :   {"cidr":"2"}
    }
)
t.add_mapping(
    "NatAMI",  {
        "us-east-1" : {"AMI" : "ami-184dc970"},
        "us-west-2" : {"AMI" : "ami-290f4119"},
        "us-west-1" : {"AMI" : "ami-1d2b2958"}
    }
)

ref_stack_id = Ref('AWS::StackId')
ref_region = Ref('AWS::Region')
ref_stack_name = Ref('AWS::StackName')

KeyName = t.add_parameter(Parameter(
    "KeyName",
    Description="Key Pair Name (for use outside of Prod)",
    Type="String",
    Default="codedeploy"
))
env = t.add_parameter(Parameter(
    "Environment",
    Type="String",
    Description="The environment being deployed into",
    Default="dev"
))
version = t.add_parameter(Parameter(
    "Version",
    Type="String",
    Description="Version",
    Default="0.1"
))
instance_type = t.add_parameter(Parameter(
    "InstanceType",
    Type="String",
    Description="Instance Type",
    Default = "t2.micro"
))
ScaleCapacity = t.add_parameter(Parameter(
    "ScaleCapacity",
    Default="1",
    Type="String",
    Description="Number of instances to initialize",
))
vpcenvcidr=10
serviceid=0
# Resources
vpc = t.add_resource(VPC(
    "VPC",
    CidrBlock=Join('', ["172.",vpcenvcidr,".0.0/16"]),
    Tags=Tags(
        Name=Join("", ["VPC-", Ref(env)])
    )
))
internetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Name=Join("", ["IGW-", Ref(env)]),
        Application=ref_stack_id,
    )
))
gatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "AttachGateway",
    VpcId=Ref(vpc),
    InternetGatewayId=Ref("InternetGateway")
))
subnet0 = t.add_resource(
    Subnet(
        'PublicSubnet0',
        CidrBlock=Join('', ['172.',vpcenvcidr,'.0.',serviceid,'/24']),
        VpcId=Ref(vpc),
        AvailabilityZone=Select("0", GetAZs(ref_region)),
        Tags=Tags(
            Name=Join("", ["Public0-", Ref(env)]),
            Application=ref_stack_id
        )
    )
)
subnet1 = t.add_resource(
    Subnet(
        'PublicSubnet1',
        CidrBlock=Join('', ['172.',vpcenvcidr,'.1.',serviceid,'/24']),
        VpcId=Ref(vpc),
        AvailabilityZone=Select("1", GetAZs(ref_region)),
        Tags=Tags(
            Name=Join("", ["Public1-", Ref(env)]),
            Application=ref_stack_id
        )
    )
)
subnet2 = t.add_resource(
    Subnet(
        'PublicSubnet2',
        CidrBlock=Join('', ['172.',vpcenvcidr,'.2.',serviceid,'/24']),
        VpcId=Ref(vpc),
        AvailabilityZone=Select("1", GetAZs(ref_region)),
        Tags=Tags(
            Name=Join("", ["Public2-", Ref(env)]),
            Application=ref_stack_id
        )
    )
)
subnet3 = t.add_resource(
    Subnet(
        'PrivateSubnet3',
        CidrBlock=Join('', ['172.',vpcenvcidr,'.3.',serviceid,'/24']),
        VpcId=Ref(vpc),
        AvailabilityZone=Select("1", GetAZs(ref_region)),
        Tags=Tags(
            Name=Join("", ["Private3-", Ref(env)]),
            Application=ref_stack_id
        )
    )
)
subnet4 = t.add_resource(
    Subnet(
        'PrivateSubnet4',
        CidrBlock=Join('', ['172.',vpcenvcidr,'.4.',serviceid,'/24']),
        VpcId=Ref(vpc),
        AvailabilityZone=Select("0", GetAZs(ref_region)),
        Tags=Tags(
            Name=Join("", ["Private4-", Ref(env)]),
            Application=ref_stack_id
        )
    )
)
subnet5 = t.add_resource(
    Subnet(
        'PrivateSubnet5',
        CidrBlock=Join('', ['172.',vpcenvcidr,'.5.',serviceid,'/24']),
        VpcId=Ref(vpc),
        AvailabilityZone=Select("0", GetAZs(ref_region)),
        Tags=Tags(
            Name=Join("", ["Private5-", Ref(env)]),
            Application=ref_stack_id
        )
    )
)

routetable = t.add_resource(RouteTable(
    "RouteTable",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name=Join("", ["RouteTable-", Ref(env)]),
        Application=ref_stack_id
    )
))

route = t.add_resource(Route(
    "Route",
    DependsOn="AttachGateway",
    RouteTableId=Ref(routetable),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(internetGateway)
))
networkacl = t.add_resource(NetworkAcl(
    "NetworkAcl",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name=Join("", ["RouteTable-", Ref(env)]),
        Application=ref_stack_id
    )
))
subnetRouteTableAssociation0 = t.add_resource(
    SubnetRouteTableAssociation(
        'SubnetRouteTableAssociationA',
        SubnetId=Ref(subnet0),
        RouteTableId=Ref(routetable),
    ))
subnetRouteTableAssociation1 = t.add_resource(
    SubnetRouteTableAssociation(
        'SubnetRouteTableAssociationB',
        SubnetId=Ref(subnet1),
        RouteTableId=Ref(routetable),
    ))
subnetRouteTableAssociation2 = t.add_resource(
    SubnetRouteTableAssociation(
        'SubnetRouteTableAssociationC',
        SubnetId=Ref(subnet2),
        RouteTableId=Ref(routetable),
    ))
sgweb = t.add_resource(SecurityGroup(
    "WebAccess",
    GroupDescription = "Access to standard web ports",
    SecurityGroupIngress = [
        SecurityGroupRule(
            IpProtocol ='tcp',
            FromPort = '80',
            ToPort = '80',
            CidrIp='0.0.0.0/0'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            FromPort = '443',
            ToPort = '443',
            CidrIp='0.0.0.0/0')
    ],
    VpcId = Ref(vpc)
))
sgelb = t.add_resource(SecurityGroup(
    "PublicELBSG",
    GroupDescription = "Access to edge instances by Public ELB",
    SecurityGroupIngress = [
        SecurityGroupRule(
            IpProtocol = 'tcp',
            FromPort = '80',
            ToPort = '80',
            SourceSecurityGroupId = Ref(sgweb)
        ),
            SecurityGroupRule(
            IpProtocol = 'tcp',
            FromPort = '443',
            ToPort = '443',
            SourceSecurityGroupId = Ref(sgweb)
        )
    ],
    VpcId = Ref(vpc)
))

sglocal = t.add_resource(SecurityGroup(
    "VPCAccess",
    GroupDescription = "VPC Access Only",
    SecurityGroupIngress = [
        SecurityGroupRule(
            IpProtocol ='-1',
            CidrIp=Join('', ['172.',vpcenvcidr,'.0.0/16']),
            FromPort = '-1',
            ToPort = '-1')
    ],
    VpcId = Ref(vpc)
))

sgtrusted = t.add_resource(SecurityGroup(
    "TrustedAccess",
    GroupDescription = "Access From Trusted Locations",
    SecurityGroupIngress = [
        SecurityGroupRule(
            IpProtocol ='-1',
            CidrIp=Join('', ['216.174.116.244/32']),
            FromPort = '-1',
            ToPort = '-1')
    ],
    VpcId = Ref(vpc)
))
sgNAT = t.add_resource(SecurityGroup(
    "NATAccess",
    GroupDescription = "NAT Access Only",
    SecurityGroupIngress = [
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp=Join('', ['172.',vpcenvcidr,'.3.',serviceid,'/24']),
            FromPort = '80',
            ToPort = '80'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp=Join('', ['172.',vpcenvcidr,'.4.',serviceid,'/24']),
            FromPort = '80',
            ToPort = '80'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp=Join('', ['172.',vpcenvcidr,'.5.',serviceid,'/24']),
            FromPort = '80',
            ToPort = '80'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp=Join('', ['172.',vpcenvcidr,'.3.',serviceid,'/24']),
            FromPort = '443',
            ToPort = '443'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp=Join('', ['172.',vpcenvcidr,'.4.',serviceid,'/24']),
            FromPort = '443',
            ToPort = '443'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp=Join('', ['172.',vpcenvcidr,'.5.',serviceid,'/24']),
            FromPort = '443',
            ToPort = '443')
    ],
    SecurityGroupEgress = [
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp='0.0.0.0/0',
            FromPort = '80',
            ToPort = '80'),
        SecurityGroupRule(
            IpProtocol ='tcp',
            CidrIp='0.0.0.0/0',
            FromPort = '443',
            ToPort = '443')
    ],
    VpcId = Ref(vpc)
))
nat = t.add_resource(Instance(
    "EnvNAT",
    ImageId=FindInMap("NatAMI",ref_region,"AMI"),
    InstanceType = Ref(instance_type),
    KeyName=Ref(KeyName),
    SourceDestCheck=False,
    SubnetId=Ref(subnet1),
    SecurityGroupIds=[Ref(sgNAT)],
    Tags=[{"Key":"Name", "Value":"EnvNAT"}],
    UserData=Base64(Join('', [
        "#cloud-config\n",
        "repo_upgrade: all\n",
        "output : { all : '| tee -a /var/log/cloud-init-output.log' }\n"
    ]))
))
natip = t.add_resource(
    EIP('natIP', InstanceId=Ref(nat)
    )
)
outputs = t.add_output([
    Output('VPC', Value=Ref(vpc)),
    Output('IGW', Value=Ref(internetGateway)),
    Output('PublicSubnet0', Value=Ref(subnet0)),
    Output('PublicSubnet1', Value=Ref(subnet1)),
    Output('SGlocal', Value=Ref(sglocal))
])

template = (t.to_json())

if __name__ == "__main__":
    print template
    file = open(filename, 'w+')
    file.write(template)
    file.close()