# Deployment

The project should be deployed to AWS under `dev_account_6` account.

1. Create ECR repo to hold docker image of the service.
2. Edit `.gitlab-ci.yml` file in the root of the project.
  There are 3 configurations in the file: dev, staging, and prod.
  Edit deploy stage of one of them you need.
  Fill
    - AWS_ECR: 270173107048.dkr.ecr.us-east-2.amazonaws.com
    - IMAGE_NAME: pearlx-api-staging
  with the values from step 1.

3. Create PostgreSQL DB in RDS.
4. Upgrade DB structure by migrations. So, this DB should have all the tables/data. See README file.
5. Create or clone existing Secret in Secrets Manager.
    Its name should be like `'pearlx-api/${suffix}/config'`,
    where suffix means dev, staging, or prod.
    Put correct settings in that secret. Like:
    ```
    "TSTREAM_DB": "Timestream database name",
    "TSTREAM_PROPS_TBL": "Timestream Properties table name",
    "TSTREAM_MEASURES_TBL": "Timestream Measures table name",
    "DATABASE_NAME": "Postgresql database name",
    "DATABASE_USERNAME": "Postgresql user name",
    "DATABASE_PASSWORD": "Postgresql password",
    "DATABASE_URL": "Postgresql connection URL",
    "JWT_KEY": "Key for JWT tokens",
    "JWT_EXPIRY_SECONDS": "JWT token expiration period in seconds",
    "DER_URI": "URL of DER utility",
    "DER_AUTH_USER": "DER user",
    "DER_AUTH_PASSWORD": "DER password",
    "DER_CERT_S3_BUCKET": "S3 bucket name with CERT for DER connection",
    "DER_CERT_S3_FILENAME": "Path to S3 file with CERT for DER connection",
    "DER_CERT_PASSWORD": "Password of CERT for DER connection",
    "SMTP_SERVER": "SMTP server hostname/IP used for sending emails in simple mode",
    "SMTP_PORT": "SMTP server port used for sending emails in simple mode",
    "SMTP_FROM": "Email address used in From field of sent emails",
    "DATABASE_HOST": "Hostname/IP of Postgresql database",
    "SQLALCHEMY_DATABASE_URI": "URL of postgresql connection used by SQL Alchemy ORM",
    "AWS_REGION": "AWS Region where the system is hosted/deployed"
    ```
    Also, See pearlx-api.yml file in could-formation sub-folder.
    There are public settings like:
    ```
    AWS_REGION: AWS Region where the system is hosted/deployed
    AWS_SECRETS_NANE: Name of secret in Secrets Manager with secret settings
    COLORED_LOGS: 1 for colored logs in output, or 0 for logs w/o colors
    EMAIL_FROM: Email address used in From field of sent emails
    FLASK_APP: run.py is the script to run application/service
    FLASK_DEBUG: 1 for add extra debug info to the logs, or 0 for w/o debug logs mode
    FLASK_ENV: production or development
    LOG_LEVEL: debug, info, or error is the level of logs to output
    SCHEDULER_ENABLED: 1 to turn on internal scheduler for update from timestream db, or 0 to turn it off
    SCHEDULER_REFRESH_FROM_TIMESTREAM: standard crontab settings like '0 0 * * *'
    ```
6. Create CloudWatch log group. Its name should be like '/ecs/pearlx-api-${suffix}'.
  See pearlx-api.yml file in could-formation sub-folder.
7. Ensure you have 2 roles: `pearlx-api-exec-role` and `pearlx-api-task-role`. Create them and policies, if it needs.
   - `pearlx-api-exec-role` has policy `pearlx-api-exec-policy`:
     ```json
         {
             "Version": "2012-10-17",
             "Statement": [
                 {
                     "Sid": "ContainerSecrets",
                     "Effect": "Allow",
                     "Action": "secretsmanager:GetSecretValue",
                     "Resource": "*"
                 },
                 {
                     "Sid": "B2BApiKey",
                     "Effect": "Allow",
                     "Action": "kms:Decrypt",
                     "Resource": "*"
                 },
                 {
                     "Sid": "CloudwatchLogs",
                     "Effect": "Allow",
                     "Action": [
                         "logs:PutLogEvents",
                         "logs:DescribeLogStreams",
                         "logs:CreateLogStream",
                         "logs:CreateLogGroup"
                     ],
                     "Resource": "*"
                 },
                 {
                     "Sid": "PullECR",
                     "Effect": "Allow",
                     "Action": [
                         "ecr:GetDownloadUrlForLayer",
                         "ecr:GetAuthorizationToken",
                         "ecr:BatchGetImage",
                         "ecr:BatchCheckLayerAvailability"
                     ],
                     "Resource": "*"
                 }
             ]
         }
     ```

   - `pearlx-api-task-role` has policies:
     - `SecretsManagerReadWrite`:	
       Provides read/write access to AWS Secrets Manager via the AWS Management Console. Note: this exludes IAM actions, so combine with IAMFullAccess if rotation configuration is required.
     - `AmazonS3ReadOnlyAccess`:
       Provides read only access to all buckets via the AWS Management Console.
     - `AmazonSESFullAccess`:
       Provides full access to Amazon SES via the AWS Management Console.
     - `AmazonRDSDataFullAccess`:
       Allows full access to use the RDS data APIs, secret store APIs for RDS database credentials, and DB console query management APIs to execute SQL statements on Aurora Serverless clusters in the AWS account.
     - `AmazonTimestreamFullAccess`:
       Provides full access to Amazon Timestream.
     - `pearlx-api-ecs-role-policy`:
       ```
       {
         "Version": "2012-10-17",
         "Statement": [
            {
              "Effect": "Allow",
              "Action": "sts:AssumeRole",
              "Resource": "arn:aws:iam::270173107048:role/pearlx-api-task-role"
            }
         ]
       }
       ```
     - `pearlx-api-task-policy`:
       ```
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Sid": "VisualEditor0",
             "Effect": "Allow",
             "Action": "timestream:*",
             "Resource": "*"
           }
         ]
       }
       ```
8. Create CloudFormation stack by pearlx-api.yml file in could-formation sub-folder.
  There are several parameter it depends on. Use values from prod.json or staging.json file.
  Wait AWS build all the objects.
  As result, there are 2 outputs:
    - `EcsService` is the name of created ECS Service;
    - `EcsSg` is its Security Group.
9. Go to Security Group of RDS DB, and put in its Inbound rules the record,
  to allow/accept PostgreSQL traffic from `EcsSg` of the service created on previous step 7.
10. Add/update in .gitlab-ci.yml file cluster name and `EcsService` from step 7:
    - CLUSTER: pearlx-api-staging
    - SERVICE: pearlx-api-staging-PearlxApiService-B3tD3qAj2S7Q
11. If your configuration has e2e-test stage (dev, staging),
  put public URL of your API:
    - CYPRESS_baseUrl: https://pearlx-api-staging-alb-622739544.us-east-2.elb.amazonaws.com/api/v1
  It's a public URL or Application Load Balancer or configure custom one like https://flextrons.io/api/v1.
12. If it uses custom Domain Name like flextrons.io,
    it needs to update A record in Route53 service for flextrons.io DNS zone
    and wait sometime to propagate changes in DNS network.
13. Use firewall.yml file in could-formation sub-folder for adding firewall rules.
    There is login requests number limit rule.
    It allows not more than 100 requests to the login route per IP per 5 minutes.
    Create a cloudformation stack by that template.
    You need to specify the ARN of ALB created by step 8.

After that there should be Swagger Web UI available on `/ui` URL.
