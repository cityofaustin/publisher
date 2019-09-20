FROM cityofaustin/publisher-base:staging-latest

ENV JANIS_BRANCH=$JANIS_BRANCH
ENV DEST=$DEST

# Clone down your Janis Branch
RUN git clone $JANIS_BRANCH
RUN yarn install --cwd ./janis

# Run your publish command
ENTRYPOINT ["./tasks/publish.sh"]
