import os, json, boto3

def janis_builder_factory(janis_branch, dest):
    codebuild = boto3.client('codebuild')

    build_config = {
        "projectName": f'coa-publisher-janis-builder-factory-{os.getenv("DEPLOY_ENV")}',
        "environmentVariablesOverride": [
            {
                "name": "JANIS_BRANCH",
                "value": os.getenv("JANIS_BRANCH"),
                "type": "PLAINTEXT"
            },
            {
                "name": "DEST",
                "value": os.getenv("DEST"),
                "type": "PLAINTEXT"
            }
        ]
    }

    res = codebuild.start_build(build_config)
