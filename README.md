# ecs-task-python-watcher
Script that polls the log of a running ECSTask to determine if the Task has completed successfully  
blog: https://nsakki55.hatenablog.com/entry/2022/06/15/233044

## usage
EcsTaskWatcher keep polling for standard output of Cloud Watch logs until the ECS Task has completed.  

```python
import boto3
from ecs_task_watcher import EcsTaskWatcher

ECS_CLUSTER = "cluster-name"
TASK_DEFINITION_ARN = "task_definition_arn"


def main():
    # Run ECS Task 
    ecs = boto3.client("ecs")
    ecs_task_reponse = ecs.run_task(
        cluster=ECS_CLUSTER,
        taskDefinition=TASK_DEFINITION_ARN,
    )
    # Pooling log until ECS Task has completed
    task_arn = ecs_task_reponse["tasks"][0]["taskArn"]
    ecs_task_watcher = EcsTaskWatcher(ECS_CLUSTER, task_arn)
    ecs_task_watcher.watch_task_condition()


if __name__ == "__main__":
    main()
```

## EcsTaskWatcher
EcsTasvekWatcher execute `describe_tasks` every 10 seconds.  
If logs have been created since the last `describe_task`, EcsTaskWatcher stdout the new logs.
```python
    def watch_task_condition(self) -> None:
        running_status = True
        while running_status:
            response = self.ecs.describe_tasks(
                cluster=self.cluster,
                tasks=[
                    self.task_arn,
                ],
            )
            last_status = response["tasks"][0]["lastStatus"]

            if last_status == "STOPPED":
                running_status = False
                self._stream_log()
                exit_code = response["tasks"][0]["containers"][0]["exitCode"]
                if exit_code == 0:
                    print("ECS Task Success")
                else:
                    print("ECS Task Failed")
                    raise ECSTaskExecutionError
            else:
                self._stream_log()
                time.sleep(10)
```
