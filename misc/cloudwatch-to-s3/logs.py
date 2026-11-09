#!/bin/env python3

import boto3
import time
from datetime import datetime

logs = boto3.client("logs")
ssm = boto3.client("ssm")


def save_logs(s3_bucket, log_group_name):
    print("LOG_GROUP=%s --> S3_BUCKET=%s" % (log_group_name, s3_bucket))
    ssm_parameter_name = ("/log-exporter-last-export/%s" % log_group_name).replace("//", "/")
    try:
        ssm_response = ssm.get_parameter(Name=ssm_parameter_name)
        ssm_value = ssm_response["Parameter"]["Value"]
    except ssm.exceptions.ParameterNotFound:
        ssm_value = "0"

    export_from_time = int(ssm_value)
    export_to_time = int(round(time.time() * 1000))

    # print("--> Exporting %s to %s" % (log_group_name, s3_bucket))

    if export_to_time - export_from_time < (23 * 60 * 60 * 1000):
        # Haven't been 23hrs from the last export of this log group
        print("    Skipped until 23hrs from last export is completed")
        return

    try:
        response = logs.create_export_task(
            logGroupName=log_group_name,
            fromTime=export_from_time,
            to=export_to_time,
            destination=s3_bucket,
            destinationPrefix=datetime.utcfromtimestamp(export_from_time / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        )
        print("    Task created: %s" % response["taskId"])
        time.sleep(5)

    except logs.exceptions.LimitExceededException:
        print("    Need to wait until all tasks are finished (LimitExceededException). Continuing later...")
        return

    except Exception as e:
        print("    Error exporting %s: %s" % (log_group_name, getattr(e, "message", repr(e))))
        return

    ssm_response = ssm.put_parameter(
        Name=ssm_parameter_name,
        Type="String",
        Value=str(export_to_time),
        Overwrite=True,
    )


if __name__ == "__main__":
    save_logs("pearlx-api-logs", "/ecs/pearlx-api")
