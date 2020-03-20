# How is Janis built?

The actual janis site building and deploying process is run by `src/janis_builder_base/scripts/build_site.sh`.

That script is first run during the build instructions for making a janis_builder docker image: `RUN ./scripts/build_site.sh` within `src/janis_builder_factory_source/janis-builder.Dockerfile`. That happens during the janis_builder_factory CodeBuild process for a build_type="rebuild".

During build_type="all_pages" or build_type="incremental", then `build_site.sh` is run when a janis_builder container is started: `ENTRYPOINT ["./scripts/build_site.sh"]` within `src/janis_builder_factory_source/janis-builder.Dockerfile`.

Look for the Dark Yellow boxes on the Publisher Diagram to see where these steps happen within the larger Publisher workflow.
