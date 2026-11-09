# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/

import boto3
from botocore.exceptions import ClientError
import requests_pkcs12
import json
import io
import time

secret_name = "SolarEdge_GS_API"
region_name = "us-east-2"


def get_secret(secret_name="SolarEdge_GS_API", region_name="us-east-2"):
    # Create a Secrets Manager client
    secretsmanager = boto3.client("secretsmanager", region_name=region_name)
    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
    try:
        get_secret_value_response = secretsmanager.get_secret_value(SecretId=secret_name)
        # get_secret_value_response = client.get_secret_value(
        #     SecretId=secret_name
        # )
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            print(e)
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            print(e)
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            print(e)
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            print(e)
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            print(e)
        return None
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        # if 'SecretString' in get_secret_value_response:
        try:
            secret = get_secret_value_response["SecretString"]
            parsed_secret = json.loads(secret)
            return parsed_secret
        except Exception as e:
            print(e)
            return None
        # else:
        #     decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])


def s3_byte(s3_resource, bucketname, filename):
    my_bucket = s3_resource.Bucket(bucketname)
    buf = io.BytesIO()
    my_bucket.download_fileobj(filename, buf)
    filecontent_bytes = buf.getvalue()
    return filecontent_bytes

    # Your code goes here.


if __name__ == "__main__":
    start = time.perf_counter()
    creds = get_secret(secret_name="SolarEdge_GS_API")
    print(creds)
    if not creds:
        raise Exception("ERROR: issue with Credentials from SecretsManager")

    s3_resource = boto3.resource("s3", region_name=region_name)
    bucketname = "apiaccesscertificates"
    filename = "solaredge/pearlx_sysadmin-solaredge-grid-services.p12"

    bytes_file = s3_byte(s3_resource, bucketname, filename)

    schedule_der_settings_update_url = (
        "https://grid-services.solaredge.com/api/utility/commands/schedule-der-settings-update"
    )

    # t = requests_pkcs12.get(url, pkcs12_data=bytes_file, pkcs12_password = creds["challenge_pwd"], auth=(creds["username"], creds["password"]))

    schedule_der_settings_update_request_header = """{
                            "derId": "83273c90-c0a8-44ec-8b15-87d10d31b5ac",
                            "startTime": "2020-05-07T10:18:12.827Z",
                            "endTime": "2020-05-07T15:18:12.827Z",
                            "eventOrigin": "GRID_SERVICES_API",
                            "priority": "1",
                            "parameters": {
                                "allowGridExport": {
                                "type": "bool",
                                "enabled": true,
                                "value": true
                                    }
                                }
                                }"""

    post_schedule_der_settings_update = requests_pkcs12.post(
        schedule_der_settings_update_url,
        json=json.loads(schedule_der_settings_update_request_header),
        pkcs12_data=bytes_file,
        pkcs12_password=creds["challenge_pwd"],
        auth=(creds["username"], creds["password"]),
    )

    print(post_schedule_der_settings_update.text)

    schedule_der_events_url = "https://grid-services.solaredge.com/api/utility/commands/schedule-der-event"

    schedule_der_events_request_header = """{
                                "derId": "f0a42cec-fb1c-406f-a173-0ce4a66980b3",
                                "commandUri": "chargeStorage",
                                "eventOrigin": "GRID_SERVICES_API",
                                "startTime": "2020-05-07T10:18:12.827Z",
                                "endTime": "2020-05-07T15:18:12.827Z",
                                "priority": "1",
                                "parameters": {
                                    "chargePowerPercent": "90"
                                }
                                }"""

    post_schedule_der_events = requests_pkcs12.post(
        schedule_der_events_url,
        json=json.loads(schedule_der_events_request_header),
        pkcs12_data=bytes_file,
        pkcs12_password=creds["challenge_pwd"],
        auth=(creds["username"], creds["password"]),
    )

    print(post_schedule_der_events.text)

    end = time.perf_counter()
    print("Execution Time:{} seconds".format(end - start))
