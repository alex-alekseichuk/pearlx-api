import boto3
from botocore.exceptions import ClientError
import requests_pkcs12
import json
import io


secret_name = "SolarEdge_GS_API"
region_name = "us-east-2"


def get_secret(secret_name="SolarEdge_GS_API", region_name="us-east-2"):

    # Create a Secrets Manager client
    # # session = boto3.session.Session(profile_name='px_ajay_default_user',region_name=region_name)
    # client = session.client(
    #     service_name='secretsmanager',
    #     region_name=region_name
    # )
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


if __name__ == "__main__":
    creds = get_secret(secret_name="SolarEdge_GS_API")
    print(creds)
    if not creds:
        raise Exception("ERROR: issue with Credentials from SecretsManager")

    s3_resource = boto3.resource("s3", region_name=region_name)
    bucket_name = "apiaccesscertificates"
    filename = "solaredge/pearlx_sysadmin-solaredge-grid-services.p12"

    bytes_file = s3_byte(s3_resource, bucket_name, filename)

    url = "https://grid-services.solaredge.com/api/utility/sites"

    t = requests_pkcs12.get(
        url, pkcs12_data=bytes_file, pkcs12_password=creds["challenge_pwd"], auth=(creds["username"], creds["password"])
    )
    print(t)
    # print(t.text)
