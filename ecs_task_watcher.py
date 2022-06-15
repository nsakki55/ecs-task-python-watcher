import time
from typing import Any, List, Tuple

import boto3


class ECSTaskExecutionError(Exception):
    """ECS Task is failed."""

    pass


class EcsTaskWatcher:
    def __init__(self, cluster: str, task_arn: str) -> None:
        self.ecs = boto3.client("ecs")
        self.cloudwatch = boto3.client("logs")
        self.cluster = cluster
        self.task_arn = task_arn

        self.log_group_name, self.log_stream_name = self._get_log_setting()

        self.previous_logs = []

    def _get_log_setting(self) -> Tuple[str, str]:
        task_description = self.ecs.describe_tasks(
            cluster=self.cluster,
            tasks=[
                self.task_arn,
            ],
        )
        task_definition_arn = task_description["tasks"][0]["taskDefinitionArn"]
        task_definition = self.ecs.describe_task_definition(taskDefinition=task_definition_arn)

        log_group_name = task_definition["taskDefinition"]["containerDefinitions"][0]["logConfiguration"]["options"][
            "awslogs-group"
        ]

        task_name = task_definition["taskDefinition"]["containerDefinitions"][0]["name"]
        log_stream_prefix = task_definition["taskDefinition"]["containerDefinitions"][0]["logConfiguration"]["options"][
            "awslogs-stream-prefix"
        ]
        task_id = self.task_arn.split("/")[-1]
        log_stream_name = f"{log_stream_prefix}/{task_name}/{task_id}"

        return log_group_name, log_stream_name

    def _stream_log(self) -> None:
        try:
            logs = self.cloudwatch.get_log_events(
                logGroupName=self.log_group_name, logStreamName=self.log_stream_name, startFromHead=True
            )["events"]

            new_logs = self._subtract_list(logs, self.previous_logs)
            if new_logs:
                for line in new_logs:
                    print(line["message"])

            self.previous_logs = logs

        except:
            pass

    def _subtract_list(self, list1, list2) -> List[Any]:
        list_diff = list1.copy()
        for l in list2:
            try:
                list_diff.remove(l)
            except ValueError:
                continue
        return list_diff

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

