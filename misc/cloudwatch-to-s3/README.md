Transfer logs
from `/ecs/pearlx-api` CloudWatch
to `pearlx-api-logs` S3 bucket.

Assume it's installed on the EC2 box with python.

Add to crontab to run it daily:

```
0 0 * * * /home/ubuntu/save-logs/logs.py >> /home/ubuntu/save-logs/save-logs.log 2>&1
```
