import os, sys, boto3
from botocore.exceptions import ClientError

# Check if yarn.lock file exists in cache for your JANIS_BRANCH

client = boto3.client('s3')
try:
    response = client.head_object(
        Bucket="coa-publisher-codebuild",
        Key=f'cache/{os.getenv("JANIS_BRANCH")}/yarn.lock'
    )
except ClientError as e:
    if e.__dict__['response']['Error']['Code'] == '404':
        print("False")
        sys.exit(0)
    else:
        raise e

exists = response['ResponseMetadata']['HTTPStatusCode'] == 200
print(exists)
