FROM cityofaustin/branch-publisher-base:staging-latest

ARG JANIS_BRANCH
ARG DEST
ENV JANIS_BRANCH=$JANIS_BRANCH
ENV DEST=$DEST

# Clone down your Janis Branch
RUN git clone -b "$JANIS_BRANCH" --single-branch https://github.com/cityofaustin/janis
RUN yarn install --cwd ./janis

# Run your publish command
ENTRYPOINT ["./tasks/publish.sh"]
