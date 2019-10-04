FROM cityofaustin/janis-builder-base:staging-latest

# Pass aws cli credentials during build
ARG AWS_DEFAULT_REGION
ARG AWS_CONTAINER_CREDENTIALS_RELATIVE_URI

# Set app-specific environment variables
ARG JANIS_BRANCH
ENV JANIS_BRANCH=$JANIS_BRANCH
ARG DEST
ENV DEST=$DEST

# Clone down your Janis Branch
RUN git clone -b "$JANIS_BRANCH" --single-branch https://github.com/cityofaustin/janis
RUN ./install_yarn_dependencies.sh

# Run your publish command
ENTRYPOINT ["./publish.sh"]
