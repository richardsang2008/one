import boto3, json, logging, time, botocore, sys, getopt, re
from boto.utils import get_instance_metadata

region = get_instance_metadata()['placement']['availability-zone'][:-1]

s3 = boto3.client('s3')
metafile='./metadata.json'
logging.basicConfig(filename='/var/log/deploy/service.log',level=logging.INFO)
cloudformation = boto3.client('cloudformation', region_name = region)

metadata=json.loads(open(metafile).read())
serviceid=metadata['service_id']
service=metadata['service_name']
version=metadata['version']
language=metadata['language']

#if language == "java":
#    from java import template as servicetemplate
#elif language == "aspnet":
if language == "aspnet":
    from aspnet import template as servicetemplate

buildbucket="rb-code-builds"
env="dev"
KeyName="codedeploy"
nat="i-5b209aad"
vpc="vpc-66803803"
ScaleCapacity="1"
sgLocal="sg-1f50517a"
subnet0="subnet-92c670e5"
subnet1="subnet-a3d242c6"
VPCAvailabilityZone0="us-west-2b"
VPCAvailabilityZone1="us-west-2a"

stack_name=service + "-" + "dev"

try:
    cloudformation.describe_stacks(StackName=stack_name)
    cfparams = [
        {'ParameterKey':'BuildBucket', 'ParameterValue' : buildbucket, 'UsePreviousValue' : False},
        {'ParameterKey':'Environment', 'ParameterValue' : env, 'UsePreviousValue' : False},
        {'ParameterKey':'KeyName', 'ParameterValue' : KeyName, 'UsePreviousValue' : False},
        {'ParameterKey':'NAT', 'ParameterValue' : nat, 'UsePreviousValue' : False},
        {'ParameterKey':'VPC', 'ParameterValue' : vpc, 'UsePreviousValue' : False},
        {'ParameterKey':'ScaleCapacity', 'ParameterValue' : ScaleCapacity, 'UsePreviousValue' : False},
        {'ParameterKey':'sgLocal', 'ParameterValue' : sgLocal, 'UsePreviousValue' : False},
        {'ParameterKey':'Subnet0', 'ParameterValue' : subnet0, 'UsePreviousValue' : False},
        {'ParameterKey':'Subnet1', 'ParameterValue' : subnet1, 'UsePreviousValue' : False},
        {'ParameterKey':'Service', 'ParameterValue' : service, 'UsePreviousValue' : False},
        {'ParameterKey':'ServiceID', 'ParameterValue' : serviceid, 'UsePreviousValue' : False},
        {'ParameterKey':'VPCAvailabilityZone0', 'ParameterValue' : VPCAvailabilityZone0, 'UsePreviousValue' : False},
        {'ParameterKey':'VPCAvailabilityZone1', 'ParameterValue' : VPCAvailabilityZone1, 'UsePreviousValue' : False}
    ]
    s3response = s3.put_object(Bucket=buildbucket, Key=stack_name+".template", Body = servicetemplate)
    try:
        print "Starting stack update..."
        logging.info("Starting Stack Update")
        cloudformation.update_stack(
            StackName=stack_name,
            TemplateURL="https://s3.amazonaws.com/{0}/{1}.template" .format(buildbucket, stack_name),
            Parameters = cfparams,
            Capabilities = ['CAPABILITY_IAM']
        )
        time.sleep(10)
        stackstate=cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
        while "IN_PROGRESS" in stackstate:
            time.sleep(10)
            stackstate=cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
            if stackstate == 'UPDATE_COMPLETE':
                print "Update Successful"
                logging.info("Stack update successful")
            elif 'FAILED' in stackstate or 'ROLLBACK' in stackstate:
                print "Stack Update failed"
                logging.error("Stack Update failed")
                sys.exit(2)
    except botocore.exceptions.ClientError as cfexception:
        if "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed." in cfexception:
            logging.info("No updates to do")
            print "Nothing to update"
        else:
            print "Unknown error occurred: %s" %cfexception
            sys.exit(2)

except botocore.exceptions.ClientError as cfexception:
#when a stack doesn't exist, it will show a message below
    if "An error occurred (ValidationError) when calling the DescribeStacks operation: Stack:%s does not exist" %stack_name in cfexception:
        print "Stack doesn't exist yet"
        cfparams = [
            {'ParameterKey':'BuildBucket', 'ParameterValue' : buildbucket, 'UsePreviousValue' : False},
            {'ParameterKey':'Environment', 'ParameterValue' : env, 'UsePreviousValue' : False},
            {'ParameterKey':'KeyName', 'ParameterValue' : KeyName, 'UsePreviousValue' : False},
            {'ParameterKey':'NAT', 'ParameterValue' : nat, 'UsePreviousValue' : False},
            {'ParameterKey':'VPC', 'ParameterValue' : vpc, 'UsePreviousValue' : False},
            {'ParameterKey':'ScaleCapacity', 'ParameterValue' : ScaleCapacity, 'UsePreviousValue' : False},
            {'ParameterKey':'sgLocal', 'ParameterValue' : sgLocal, 'UsePreviousValue' : False},
            {'ParameterKey':'Subnet0', 'ParameterValue' : subnet0, 'UsePreviousValue' : False},
            {'ParameterKey':'Subnet1', 'ParameterValue' : subnet1, 'UsePreviousValue' : False},
            {'ParameterKey':'Service', 'ParameterValue' : service, 'UsePreviousValue' : False},
            {'ParameterKey':'ServiceID', 'ParameterValue' : serviceid, 'UsePreviousValue' : False},
            {'ParameterKey':'VPCAvailabilityZone0', 'ParameterValue' : VPCAvailabilityZone0, 'UsePreviousValue' : False},
            {'ParameterKey':'VPCAvailabilityZone1', 'ParameterValue' : VPCAvailabilityZone1, 'UsePreviousValue' : False}
        ]
        s3response = s3.put_object(Bucket=buildbucket, Key=stack_name+".template", Body = servicetemplate)
        cf2response = cloudformation.create_stack(
            StackName=stack_name,
            TemplateURL="https://s3.amazonaws.com/{0}/{1}.template" .format(buildbucket, stack_name),
            Parameters=cfparams,
            Capabilities=['CAPABILITY_IAM']
        )
        time.sleep(10)
        stackstate=cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
        while "IN_PROGRESS" in stackstate:
            time.sleep(10)
            stackstate=cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
            if stackstate == 'CREATE_COMPLETE':
                print "Stack created succesfully in Cloudformation"
                logging.info("Stack creation successful")
            elif 'FAILED' in stackstate or 'ROLLBACK' in stackstate:
                print "Stack creation failed"
                sys.exit(2)
            logging.info("Stack Creation Complete")
