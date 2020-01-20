import os, json, boto3
from botocore.exceptions import ClientError

# Create a temporary bastion server to tunnel into Private RDS
def deploy_bastion():
    ec2_client = boto3.client('ec2')
    cf_client = boto3.client('cloudformation')
    main_stack_name = f'coa-publisher-{os.getenv("DEPLOY_ENV")}'
    bastion_stack_name = f'{main_stack_name}-bastion'

    # Check if bastion stack needs to be created or updated
    try:
        cf_client.describe_stacks(StackName=bastion_stack_name)
        bastion_exists = True
    except ClientError:
        bastion_exists = False

    # Create key to use to access Bastion server
    BastionKeyName = f'coa-publisher-{os.getenv("DEPLOY_ENV")}-bastion-key'
    if not bastion_exists:
        res = ec2_client.create_key_pair(
            KeyName=BastionKeyName,
        )
        pem_file_path = os.path.join(os.path.dirname(__file__), f'./{BastionKeyName}.pem')
        pem_file = open(pem_file_path, "w")
        pem_file.write(res['KeyMaterial'])
        pem_file.close()
        os.chmod(pem_file_path, 400)

    # Read template.yml
    template_file = open(os.path.join(os.path.dirname(__file__), './template.yml'),"r")
    template = template_file.read()
    template_file.close()



    # Get Parameters from coa-publisher stack outputs
    cf_outputs = cf_client.describe_stacks(
        StackName=main_stack_name
    )['Stacks'][0]['Outputs']
    for x in cf_outputs:
        if x['OutputKey'] == "VPCId":
            VPCId = x["OutputValue"]
        if x['OutputKey'] == "PublicSubnetOne":
            SubnetId = x["OutputValue"]
        if x['OutputKey'] == "ClusterSecurityGroup":
            ClusterSecurityGroup = x["OutputValue"]
        if x['OutputKey'] == "PublicSubnetOneAz":
            PublicSubnetOneAz = x["OutputValue"]

    if bastion_exists:
        build_command = cf_client.update_stack
    else:
        build_command = cf_client.create_stack
    res = build_command(
        StackName=bastion_stack_name,
        TemplateBody=template,
        Parameters=[
            {
                "ParameterKey": "VPCId",
                "ParameterValue": VPCId,
            },
            {
                "ParameterKey": "SubnetId",
                "ParameterValue": SubnetId,
            },
            {
                "ParameterKey": "ClusterSecurityGroup",
                "ParameterValue": ClusterSecurityGroup,
            },
            {
                "ParameterKey": "BastionKeyName",
                "ParameterValue": BastionKeyName,
            },
        ],
        Capabilities=['CAPABILITY_NAMED_IAM'],
        Tags=[
            {
                "Key": "user:app",
                "Value": "publisher",
            },
            {
                "Key": "user:stage",
                "Value": os.getenv("DEPLOY_ENV"),
            },
            {
                "Key": "user:project",
                "Value": "alpha.austin.gov",
            },
        ],
    )

    # Wait for completion
    if bastion_exists:
        waiter = cf_client.get_waiter('stack_update_complete')
    else:
        waiter = cf_client.get_waiter('stack_create_complete')

    try:
        print(f"Building {bastion_stack_name}...")
        waiter.wait(
            StackName=bastion_stack_name,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 120,
            }
        )
        print("Bastion stack finished building.")
    except WaiterError as e:
        print(e.message)
        raise e

deploy_bastion()
