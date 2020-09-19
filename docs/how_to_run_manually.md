# How to Run Manually

There might come times when a developer might want to invoke the Publisher manually. We have a couple of scripts to help with that.

`pipenv run python src/utils/test_send_request.py` will send a publish_request POST request to your stack's publish_request lambda function.

`pipenv run python src/utils/test_start_build.py` will manually start a build. There is no public endpoint to start a build, so it will call the command directly, bypassing the publish_request handler.

## How to set params
The parameters for these functions are environment variables that must be set in your .env file. The section `# For dev utils` contains vars that are only used for these util functions, not for the deployment scripts.

- `DEPLOY_ENV` determines which deployed Publisher stack you want to invoke. (This var is also used for deployment scripts).
- `JANIS_BRANCH` and `JOPLIN` set the Janis branch you want to build, and the Joplin deployment you want to fetch data from.
- `COA_PUBLISHER_DEV_API_KEY` is the api key that we can use for our own personal manual invocations. Every publish_request request must have a valid API Key to authenticate it. Our serverless.yml stack defines 3 apiKeys:

```
apiKeys:
  - name: coa-publisher-${env:DEPLOY_ENV}-janis
    description: "API key for requests from janis github pushes"
  - name: coa-publisher-${env:DEPLOY_ENV}-joplin
    description: "API key for requests from joplin"
  - name: coa-publisher-${env:DEPLOY_ENV}-dev
    description: "API key for requests manually initiated by devs"
```

You're going to want to use the "-dev" key. The values for these keys is kept secret, there can be found in AWS => Stacks => coa-publisher-{DEPLOY_ENV} => Resources => ApiGatewayApiKey3.

- `PUBLISH_REQUEST_URL` is the URL for triggered the "publish_request" lambda function. This can be found in AWS => Cloudformation => Stacks => coa-publisher-{DEPLOY_ENV} => Outputs => PublishRequestEndpoint.
