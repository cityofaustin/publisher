import os, pathlib, boto3

cf_client = boto3.client('cloudformation')
dir = str(pathlib.Path(__file__).parent.absolute())

# Get JANIS_BUILDER_BASE_ECR_URI from stack outputs
# Write output to a file that can be sourced by deploy.sh script
cf_outputs = cf_client.describe_stacks(
    StackName=f'coa-publisher-persistent-infrastructure'
)['Stacks'][0]['Outputs']
for x in cf_outputs:
    if x['OutputKey'] == "JanisBuilderBaseEcrUri":
        JANIS_BUILDER_BASE_ECR_URI = x["OutputValue"]
        f = open(f"{dir}/ecr_uri.tmp","w+")
        f.write(f"JANIS_BUILDER_BASE_ECR_URI={JANIS_BUILDER_BASE_ECR_URI}\n")
        f.close()

if not JANIS_BUILDER_BASE_ECR_URI:
    exit(1)
