ARG VERSION
ARG JANIS_BUILDER_BASE_ECR_URI
FROM $JANIS_BUILDER_BASE_ECR_URI:$VERSION

# Pass aws cli credentials during build
ARG AWS_DEFAULT_REGION
ARG AWS_CONTAINER_CREDENTIALS_RELATIVE_URI

# Set app-specific environment variables
ARG JANIS_BRANCH
ENV JANIS_BRANCH=$JANIS_BRANCH
ARG DEST
ENV DEST=$DEST
ARG CMS_MEDIA
ENV CMS_MEDIA=$CMS_MEDIA

# Clone down your Janis Branch
RUN git clone -b "$JANIS_BRANCH" --single-branch https://github.com/cityofaustin/janis
RUN ./scripts/install_yarn_dependencies.sh

# Run your publish command
ENTRYPOINT ["./scripts/publish.sh"]
