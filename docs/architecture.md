## ECS

The Elastic Container Service (ECS) is necessary in order to launch Fargate tasks. These tasks are the containers that actually run your janis build commands.

The CloudFormation instructions for building your ECS stack are located in `ecs/ecs_cluster.yml`.

Deploy those ECS instructions by running `ecs/deploy.sh`.
