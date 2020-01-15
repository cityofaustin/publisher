import os, json, boto3

def start_janis_builder_factory(janis_branch, dest):
    codebuild = boto3.client('codebuild')

    res = codebuild.start_build(
        projectName=f'coa-publisher-janis-builder-factory-{os.getenv("DEPLOY_ENV")}',
        environmentVariablesOverride=[
            {
                "name": "JANIS_BRANCH",
                "value": janis_branch,
                "type": "PLAINTEXT"
            },
            {
                "name": "DEST",
                "value": dest,
                "type": "PLAINTEXT",
            },
        ],
    )

    print(res)
