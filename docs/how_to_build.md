- Install aws cli and add crendentials to your machine.
- Build a ECS cluster.
  - `sh ./cloudFormation/deploy_ecs_cluster.sh`
  - The Elastic Container Service cluster is where your tasks will be launched from. "Tasks" are worker docker containers that do a task.