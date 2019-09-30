import os, json

start_build_config = {
    "projectName": f'coa-branch-publisher-builder-{os.getenv("DEPLOY_ENV")}',
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
start_build_file = os.path.join(os.path.dirname(__file__), './start-build.json')

with open(start_build_file, 'w') as outfile:
    json.dump(start_build_config, outfile)
