import os, json, boto3

# Destroy the bastion stack when you're done looking at RDS
def destroy_bastion():
    ec2_client = boto3.client('ec2')
    cf_client = boto3.client('cloudformation')

    # Delete the key used to access Basion server
    BastionKeyName = f'coa-publisher-{os.getenv("DEPLOY_ENV")}-bastion-key'
    ec2_client.delete_key_pair(
        KeyName=BastionKeyName
    )

    # Delete .pem file
    os.remove(os.path.join(os.path.dirname(__file__), f'./{BastionKeyName}.pem'))

    # Delete Bastion stack
    cf_client.delete_stack(
        StackName=f'coa-publisher-{os.getenv("DEPLOY_ENV")}-bastion',
    )

destroy_bastion()
