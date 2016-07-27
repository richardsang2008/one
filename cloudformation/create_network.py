import os

from troposphere import Template,Tags,Parameter,Join, Ref
from troposphere.ec2 import VPC,InternetGateway
#varible can be refactored later
vpc_cidr = "172.16.0.0/27"

t = Template()

def GenerateNetworkTemplate():
    t.add_description("GD Network Infrastructure")
    env = t.add_parameter(Parameter("Environment", Type="String", Description="Demo deplyment environment", Default="dev"))
    t.add_resource(VPC("VPC", CidrBlock=vpc_cidr, EnableDnsHostnames = True, Tags = Tags(Name=Join("",[Ref(env),"_VPC"]))))
    t.add_resource(InternetGateway("InternetGateway", Tags = Tags(Name=Join("",[Ref(env),"_InternetGateway"]))))


if __name__ == '__main__':
    GenerateVPCTemplate()
    template = t.to_json()
    directory = "vpc_template"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = directory + "/vpc.template"
    file = open(filename, 'w+')
    file.write(template)
    file.close()
