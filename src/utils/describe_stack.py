import os, json, boto3, time

cf_client = boto3.client('cloudformation')

# This script is just a developer utility for viewing Stack Outputs.
# It's not called by any automated process.

start = time.time()

# Log the CloudFormation stack outputs that you need to enter as environment variables
cf_outputs = cf_client.describe_stacks(
    StackName=f'coa-publisher-{os.getenv("DEPLOY_ENV")}'
)['Stacks'][0]['Outputs']

for x in cf_outputs:
    print(x)

end = time.time()
print(end - start)
