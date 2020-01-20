import os, json, boto3

# Creates instructions for a developer to tunnel into private Publisher Database.
# You must manually generate start an ssh tunnel into the database's private subnet through the bastion server.
# Make sure you destroy the bastion server (destory.py) when you're done investigating.
def get_bastion_dns():
    cf_client = boto3.client('cloudformation')
    main_stack_name = f'coa-publisher-{os.getenv("DEPLOY_ENV")}'
    bastion_stack_name = f'{main_stack_name}-bastion'

    cf_outputs = cf_client.describe_stacks(
        StackName=bastion_stack_name
    )['Stacks'][0]['Outputs']
    for x in cf_outputs:
        if x['OutputKey'] == "BastionDns":
            bastion_dns = x["OutputValue"]

    cf_outputs = cf_client.describe_stacks(
        StackName=main_stack_name
    )['Stacks'][0]['Outputs']
    for x in cf_outputs:
        if x['OutputKey'] == "PgEndpoint":
            pg_endpoint = x["OutputValue"]

    tunnel_port = 9000
    print("Create an ssh tunnel with:")
    print(f'ssh -i "coa-publisher-staging-bastion-key.pem" -NL {tunnel_port}:{pg_endpoint}:5432 ubuntu@{bastion_dns} -v')
    print('\n')
    print(f'Then connect to the coa-publisher-{os.getenv("DEPLOY_ENV")} database with:')
    print(f'psql -h localhost -p {tunnel_port} -U {os.getenv("RDS_MASTER_USERNAME") or "[username]"}')

get_bastion_dns()
