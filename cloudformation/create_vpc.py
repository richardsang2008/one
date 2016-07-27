import os

from troposphere import Template, Tags, Parameter, Join, Ref, Output, GetAZs,FindInMap,Base64
from troposphere.ec2 import VPC, InternetGateway, RouteTable, NetworkAcl, Route, Subnet, VPNGateway, SubnetNetworkAclAssociation,SubnetRouteTableAssociation, \
    NetworkAclEntry, PortRange, VPCGatewayAttachment

import troposphere.ec2 as ec2

import troposphere.elasticloadbalancing as elb

# varible can be refactored later
vpcenvcidr = 16
serviceid = 0

vpc_cidr = Join("",["172.",vpcenvcidr,".0.0/27"])

ref_stack_id = Ref('AWS::StackId')
t = Template()
t.add_description("GD Cloud Infrastructure")
env = t.add_parameter(Parameter("Environment", Type="String", Description="Demo deplyment environment", Default="dev"))
vpc = None
privateSubnet1 = None
privateSubnet2 = None
privateSubnet3 = None
privateSubnet4 = None
privateSubnet5 = None
privateSubnet6 = None
publicSubnet1 = None
publicSubnet2 = None
internetGateway = None


def generate_vpc_template():
    global vpc
    vpc = t.add_resource(VPC(
        "VPC",
        EnableDnsSupport="true",
        CidrBlock=vpc_cidr,
        EnableDnsHostnames=True,
        Tags=Tags(
            Application=Ref(env),
            Network=Join("", [Ref(env),"_VPC"])
        )
    ))


def generate_netowrk_template():
    global  internetGateway
    internetGateway = t.add_resource(InternetGateway(
        "InternetGateway",
        Tags=Tags(
            Name=Join("", [ Ref(env), "_IneterNetGateway",]),
            Application=ref_stack_id,
        )
    ))
    gatewayAttachment = t.add_resource(VPCGatewayAttachment(
        "AttachGateway",
        VpcId=Ref(vpc),
        InternetGatewayId=Ref("InternetGateway")
    ))

    publicRouteTable = t.add_resource(RouteTable(
        "PublicRouteTable",
        VpcId=Ref(vpc),
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_PublicRouteTable"])
        )
    ))



    privateRouteTable = t.add_resource(RouteTable(
        "PrivateRouteTable",
        VpcId=Ref(vpc),
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_PrivateRouteTable"])
        )
    ))

    privateNetworkAcl = t.add_resource(NetworkAcl(
        "PrivateNetworkAcl",
        VpcId=Ref(vpc),
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_PrivateNetworkAcl"])
        )
    ))



    route = t.add_resource(Route(
        "Route",
        GatewayId=Ref(internetGateway),
        DestinationCidrBlock="0.0.0.0/0",
        RouteTableId=Ref(privateRouteTable),
    ))
   #define 2 public public subnet
    global  publicSubnet1
    publicSubnet1 = t.add_resource(Subnet(
        "PublicSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network= Join("", [Ref(env), "_Public Subnet 1"]),
        )
    ))
    global publicSubnet2
    publicSubnet2 = t.add_resource(Subnet(
        "PublicSubnet2",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Public Subnet 2"])
        )
    ))
    # publicSubnets=[2]
    # publicSubnets[0]= publicSubnet1
    # publicSubnets[1] = publicSubnet2
    #define 6 private subnet
    global privateSubnet1
    privateSubnet1 = t.add_resource(Subnet(
        "PrivateSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet1"])
        )
    ))
    global privateSubnet2
    privateSubnet2 = t.add_resource(Subnet(
        "PrivateSubnet2",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 2"])
        )
    ))
    global privateSubnet3
    privateSubnet3 = t.add_resource(Subnet(
        "PrivateSubnet3",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 3"])
        )
    ))
    global privateSubnet4
    privateSubnet4 = t.add_resource(Subnet(
        "PrivateSubnet4",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 4"])
        )
    ))
    global privateSubnet5
    privateSubnet5 = t.add_resource(Subnet(
        "PrivateSubnet5",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 5"])
        )
    ))
    global privateSubnet6
    privateSubnet6 = t.add_resource(Subnet(
        "PrivateSubnet6",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 6"])
        )
    ))

    # privateSubnets = [6]
    # privateSubnets[0] = privateSubnet1
    # privateSubnets[1] = privateSubnet2
    # privateSubnets[2] = privateSubnet3
    # privateSubnets[3] = privateSubnet4
    # privateSubnets[4] = privateSubnet5
    # privateSubnets[5] = privateSubnet6



    privateSubnetNetworkAclAssociation1 = t.add_resource(
         SubnetNetworkAclAssociation(
             "PrivateSubnetNetworkAclAssociation",
             SubnetId=Ref(privateSubnet1),
             NetworkAclId=Ref(privateNetworkAcl),
         )
     )


    privateSubnetRouteTableAssociation1 = t.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnetRouteTableAssociation1",
            SubnetId=Ref(privateSubnet1),
            RouteTableId=Ref(privateRouteTable),
        )
    )
    privateSubnetRouteTableAssociation2 = t.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnetRouteTableAssociation2",
            SubnetId=Ref(privateSubnet2),
            RouteTableId=Ref(privateRouteTable),
        )
    )
    privateSubnetRouteTableAssociation3 = t.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnetRouteTableAssociation3",
            SubnetId=Ref(privateSubnet3),
            RouteTableId=Ref(privateRouteTable),
        )
    )
    privateSubnetRouteTableAssociation4 = t.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnetRouteTableAssociation4",
            SubnetId=Ref(privateSubnet4),
            RouteTableId=Ref(privateRouteTable),
        )
    )
    privateSubnetRouteTableAssociation5 = t.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnetRouteTableAssociation5",
            SubnetId=Ref(privateSubnet5),
            RouteTableId=Ref(privateRouteTable),
        )
    )
    privateSubnetRouteTableAssociation6 = t.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnetRouteTableAssociation6",
            SubnetId=Ref(privateSubnet6),
            RouteTableId=Ref(privateRouteTable),
        )
    )
    publicSubnetRouteTableAssociation1 = t.add_resource(
        SubnetRouteTableAssociation(
            "PublicSubnetRouteTableAssociation1",
            SubnetId=Ref(publicSubnet1),
            RouteTableId=Ref(publicRouteTable),
        )
    )
    publicSubnetRouteTableAssociation2 = t.add_resource(
        SubnetRouteTableAssociation(
            "PublicSubnetRouteTableAssociation2",
            SubnetId=Ref(publicSubnet2),
            RouteTableId=Ref(publicRouteTable),
        )
    )


    OutBoundPrivateNetworkAclEntry = t.add_resource(NetworkAclEntry(
        "OutBoundPrivateNetworkAclEntry",
        NetworkAclId=Ref(privateNetworkAcl),
        RuleNumber="100",
        Protocol="6",
        PortRange=PortRange(To="65535", From="0"),
        Egress="true",
        RuleAction="allow",
        CidrBlock="0.0.0.0/0",
    ))


def generate_ec2_template():
    # Add the Parameters
    keyname_param = t.add_parameter(Parameter(
        "KeyName",
        Type="String",
        Default="mark",
        Description="Name of an existing EC2 KeyPair to "
                    "enable SSH access to the instance",
    ))

    t.add_parameter(Parameter(
        "InstanceType",
        Type="String",
        Description="WebServer EC2 instance type",
        Default="m1.small",
        AllowedValues=[
            "t1.micro", "m1.small", "m1.medium", "m1.large", "m1.xlarge",
            "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "c1.medium", "c1.xlarge",
            "cc1.4xlarge", "cc2.8xlarge", "cg1.4xlarge"
        ],
        ConstraintDescription="must be a valid EC2 instance type.",
    ))

    webport_param = t.add_parameter(Parameter(
        "WebServerPort",
        Type="String",
        Default="8888",
        Description="TCP/IP port of the web server",
    ))

    # Define the instance security group
    instance_sg = t.add_resource(
        ec2.SecurityGroup(
            "InstanceSecurityGroup",
            GroupDescription="Enable SSH and HTTP access on the inbound port",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="22",
                    ToPort="22",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=Ref(webport_param),
                    ToPort=Ref(webport_param),
                    CidrIp="0.0.0.0/0",
                ),
            ]
        )
    )

    # Add the web server instances
    web_instances = []
    for name in ("Ec2Instance1", "Ec2Instance2"):
        instance = t.add_resource(ec2.Instance(
            name,
            SecurityGroups=[Ref(instance_sg)],
            KeyName=Ref(keyname_param),
            InstanceType=Ref("InstanceType"),
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
            UserData=Base64(Ref(webport_param)),
        ))
        web_instances.append(instance)

    elasticLB = t.add_resource(elb.LoadBalancer(
        'ElasticLoadBalancer',
        AvailabilityZones=GetAZs(""),
        ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
            Enabled=True,
            Timeout=300,
        ),
        Instances=[Ref(r) for r in web_instances],
        Listeners=[
            elb.Listener(
                LoadBalancerPort="80",
                InstancePort=Ref(webport_param),
                Protocol="HTTP",
            ),
        ],
        HealthCheck=elb.HealthCheck(
            Target=Join("", ["HTTP:", Ref(webport_param), "/"]),
            HealthyThreshold="3",
            UnhealthyThreshold="5",
            Interval="30",
            Timeout="5",
        )
    ))


if __name__ == '__main__':
    generate_vpc_template()
    generate_netowrk_template()
    generate_ec2_template()
    template = t.to_json()
    directory = "vpc_template"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = directory + "/vpc.template"
    file = open(filename, 'w+')
    file.write(template)
    file.close()
