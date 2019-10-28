<p align="center">
  <img src="/docs/images/publishing_house.jpg" width="300" >
</p>

# coa-publisher-mvp

The Publisher is a microservice used to manage Janis PR deployments on netlify. It allows you to plug in your own environment variables into Janis deployments. It also enables publishing from Joplin PR builds to Janis PR builds.

## The Architecture

The only code you care about is in `/src/coa-publisher-mvp`. This contains all the code you need to run the MVP publisher (netlify PRs only).

The other directories in `src` contain work-in-progress components for handling Production and Staging builds on AWS. You can ignore them for now.

coa-publisher-mvp is a `flask` python server deployed as a serverless function with `Zappa`. It has these 2 routes:

### /build
- Creates a new Netlify site for a Janis Branch.
- Will not re-create a netlify site if one already exists for your branch.
- Updates environment variables whether the site exists or not.
- src/coa-publisher-mvp/src/views/build.py
  #### Params:
  - janis_branch: (required), the name of the Janis Branch you want to deploy
  - CMS_API: (required), the URL of the Joplin graphql API endpoint you want Janis to build off of.
  - CMS_MEDIA: (optional), address of the S3 bucket you want to use to get static media
  - CMS_DOCS: (optional), flag for CMS_DOCS on Janis
  - DEPLOYMENT_MODE: (optional), flag for DEPLOYMENT_MODE on Janis
  #### Sample Request to Local Server:
  curl -d '{"janis_branch": "3010-circleci", "CMS_API": "https://joplin-staging.herokuapp.com/api/graphql"}' -X POST localhost:5000/build

### /publish
- Updates environment variables
- Triggers a publish_hook on a netlify site created by /build
- A publish hook will rebuild the entire Janis PR site from your specified CMS_API.
- src/coa-publisher-mvp/src/views/publish.py
  #### Params:
  - The same as /build
  #### Sample Request to Local Server:
  curl -d '{"janis_branch": "3010-circleci", "CMS_API": "https://joplin-staging.herokuapp.com/api/graphql"}' -X POST localhost:5000/publish

## Running Locally

You can set up an instance of coa-publisher-mvp locally. It will have the full capability of building and publishing any Janis branch on netlify. You won't have the ability to mess with staging or production (because they are hosted on AWS and not netlify), but you will have the ability to tamper with other people's PR builds. Here's what you need to do!

### 1. Install python dependencies
`pipenv install`

### 2. Set up your environment variables

Copy the template.env to .env and plug in your desired environment variables. This will allow your environment variables to get picked up by pipenv.

`cp template.env .env`

The environment vars we use are committed in the AWS Systems Manager. https://console.aws.amazon.com/systems-manager/parameters/?region=us-east-1

- NETLIFY_AUTH_TOKEN
  - `/coa-publisher/mvp/NETLIFY_AUTH_TOKEN` in AWS Systems Manager
  - Personal Access Token for our netlify API. They can be found/created in the Netlify dashboard under User Settings > Applications > Personal Access Tokens.
- NETLIFY_GITHUB_INSTALLATION_ID
  - `/coa-publisher/mvp/NETLIFY_GITHUB_INSTALLATION_ID` in AWS Systems Manager
  - Originally copy and pasted from another Janis site that had a manually created github integration. It can be found under build_settings.installation_id in api response from https://api.netlify.com/api/v1/sites/{site_id}
- DEPLOY_ENV and JANIS_BRANCH are unused by coa-publisher-mvp, but they will be used in the next version of the Publisher.

### 3. Run it
`sh /src/coa-publisher-mvp/scripts/run-local.sh`

## Deployment

I didn't feel like setting up automated deployment for the MVP, so deployments are handled manually.

These steps will update the `coa-publisher-mvp-pr` AWS stack and lambda functions.
If you need to debug a deployment that went awry, you can run `sh /src/coa-publisher-mvp/scripts/check-zappa-logs.sh`

### 1. Add the right environment variables to .env
Follow the above steps

### 2. Make sure you have your aws-cli credentials set up locally
`cat ~/.aws/credentials`

### 3. Deploy it
`sh /src/coa-publisher-mvp/deploy/deploy.sh`
