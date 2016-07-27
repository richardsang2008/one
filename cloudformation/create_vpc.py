import os

from troposphere import Template, Tags, Parameter, Join, Ref, Output
from troposphere.ec2 import VPC, InternetGateway, RouteTable, NetworkAcl, Route, Subnet, VPNGateway, SubnetNetworkAclAssociation,SubnetRouteTableAssociation, \
    NetworkAclEntry, PortRange

# varible can be refactored later
vpcenvcidr = 16
serviceid = 0

vpc_cidr = Join("",["172.",vpcenvcidr,".0.0/27"])

ref_stack_id = Ref('AWS::StackId')
t = Template()
t.add_description("GD Cloud Infrastructure")
env = t.add_parameter(Parameter("Environment", Type="String", Description="Demo deplyment environment", Default="dev"))
vpc = None


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


    vpnGateway = t.add_resource(VPNGateway(
        "VPNGateway",
        Type="ipsec.1",
        Tags=Tags(
            Application=Ref(env),
        )
    ))
    route = t.add_resource(Route(
        "Route",
        GatewayId=Ref(vpnGateway),
        DestinationCidrBlock="0.0.0.0/0",
        RouteTableId=Ref(privateRouteTable),
    ))
   #define 2 public public subnet
    publicSubnet1 = t.add_resource(Subnet(
        "PublicSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network= Join("", [Ref(env), "_Public Subnet 1"]),
        )
    ))

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
    privateSubnet1 = t.add_resource(Subnet(
        "PrivateSubnet1",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet1"])
        )
    ))

    privateSubnet2 = t.add_resource(Subnet(
        "PrivateSubnet2",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 2"])
        )
    ))
    privateSubnet3 = t.add_resource(Subnet(
        "PrivateSubnet3",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 3"])
        )
    ))
    privateSubnet4 = t.add_resource(Subnet(
        "PrivateSubnet4",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 4"])
        )
    ))
    privateSubnet5 = t.add_resource(Subnet(
        "PrivateSubnet5",
        VpcId=Ref(vpc),
        CidrBlock="0.0.0.0/30",
        Tags=Tags(
            Application=ref_stack_id,
            Network=Join("", [Ref(env), "_Private Subnet 5"])
        )
    ))
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
    # outputs = t.add_output(Output(
    #     "VPCId",
    #     Description="VPCId of the newly created VPC",
    #     Value=Ref(VPC),
    # ))


outputs = t.add_output([
    Output('VPC', Value=Ref(vpc)),
    # Output('IGW', Value=Ref(internetGateway)),
    Output('PublicSubnet1', Value=Ref("PublicSubnet1")),
    Output('PublicSubnet2', Value=Ref("PublicSubnet2")),
    Output('PrivateSubnet1', Value=Ref("PrivateSubnet1")),
    Output('PrivateSubnet2', Value=Ref("PrivateSubnet2")),
    Output('PrivateSubnet3', Value=Ref("PrivateSubnet3")),
    Output('PrivateSubnet4', Value=Ref("PrivateSubnet4")),
    Output('PrivateSubnet5', Value=Ref("PrivateSubnet5")),
    Output('PrivateSubnet6', Value=Ref("PrivateSubnet6")),

    # Output('SGlocal', Value=Ref(sglocal))
])

template = (t.to_json())
if __name__ == '__main__':
    generate_vpc_template()
    generate_netowrk_template()

    template = t.to_json()
    directory = "vpc_template"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = directory + "/vpc.template"
    file = open(filename, 'w+')
    file.write(template)
    file.close()
