1. Janis Branch gets pushed to github.
2. A build docker image gets made for that branch.
  - try to get cached yarn modules.
  - run yarn build
3. Docker image gets pushed to AWS ECR.

4. Publisher gets a request to build.
5. Spins up a build docker image.
6. Runs build process.
  - Copies down /dist folder if its an incremental build
7. Copies /dist folder to S3.
  - PR: also copies to netlify
  - Staging/Prod: does a Cloudfront cache invalidation
