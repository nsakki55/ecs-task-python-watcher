import boto3
from ecs_task_watcher import EcsTaskWatcher

ECS_CLUSTER = "cluster-name"
TASK_DEFINITION_ARN = "task_definition_arn"


def main():
    ecs = boto3.client("ecs")
    ecs_task_reponse = ecs.run_task(
        cluster=ECS_CLUSTER,
        taskDefinition=TASK_DEFINITION_ARN,
    )

    task_arn = ecs_task_reponse["tasks"][0]["taskArn"]
    ecs_task_watcher = EcsTaskWatcher(ECS_CLUSTER, task_arn)
    ecs_task_watcher.watch_task_condition()


if __name__ == "__main__":
    main()
