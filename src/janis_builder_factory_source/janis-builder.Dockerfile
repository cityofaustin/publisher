ARG VERSION
ARG JANIS_BUILDER_BASE_ECR_URI
FROM $JANIS_BUILDER_BASE_ECR_URI:$VERSION

# Pass aws cli credentials during build
ARG AWS_DEFAULT_REGION
ARG AWS_CONTAINER_CREDENTIALS_RELATIVE_URI

# Set NETLIFY_AUTH_TOKEN for netlify sdk
ARG NETLIFY_AUTH_TOKEN
ENV NETLIFY_AUTH_TOKEN=$NETLIFY_AUTH_TOKEN

# Set app-specific environment variables
ARG JANIS_BRANCH
ENV JANIS_BRANCH=$JANIS_BRANCH
ARG BUILD_ID
ENV BUILD_ID=$BUILD_ID
ARG DEPLOYMENT_MODE
ENV DEPLOYMENT_MODE=$DEPLOYMENT_MODE
ARG CMS_API
ENV CMS_API=$CMS_API
ARG CMS_MEDIA
ENV CMS_MEDIA=$CMS_MEDIA
ARG CMS_DOCS
ENV CMS_DOCS=$CMS_DOCS
ARG GOOGLE_ANALYTICS
ENV GOOGLE_ANALYTICS=$GOOGLE_ANALYTICS
ARG NETLIFY_SITE_NAME
ENV NETLIFY_SITE_NAME=$NETLIFY_SITE_NAME
ARG CLOUDFRONT_DISTRIBUTION_ID
ENV CLOUDFRONT_DISTRIBUTION_ID=$CLOUDFRONT_DISTRIBUTION_ID

# Set additional optional env_vars
ARG REACT_STATIC_PREFETCH_RATE
ENV REACT_STATIC_PREFETCH_RATE=$REACT_STATIC_PREFETCH_RATE

# Clone down your Janis Branch
RUN git clone -b "$JANIS_BRANCH" --single-branch https://github.com/cityofaustin/janis
RUN ./scripts/install_yarn_dependencies.sh

# Run initial build_site command
ENV BUILD_TYPE="rebuild"
RUN ./scripts/build_site.sh

# Set Entrypoint to build_site.sh for future Fargate invocations
ENTRYPOINT ["./scripts/build_site.sh"]
