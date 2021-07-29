import segno
import json
import logging
import os
import boto3
from string import Template

logger = logging.getLogger()
logger.setLevel(logging.INFO)

qr_code_bucket = os.environ['QRCodeBucketName']


def handler(event, context):
    logger.info(event)
    stage = event['requestContext']['stage']
    request_body = json.loads(event['body'])
    file_name = Template('$name.$extension').safe_substitute(name=request_body['qr-code-name'],
                                                             extension=request_body['file-type'])
    file_path = Template('$stage/$name').safe_substitute(stage=stage, name=file_name)
    temp_file = Template('/tmp/$name').safe_substitute(name=file_name)
    content_type = Template('image/$type').safe_substitute(type=request_body['file-type'])

    qr_code = segno.make(request_body['data'], micro=request_body['micro'])
    qr_code.save(temp_file, scale=request_body['scale'])

    url = Template('https://$bucketName.s3.amazonaws.com/$path').safe_substitute(bucketName=qr_code_bucket,
                                                                                 path=file_path)

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(temp_file, qr_code_bucket, file_path, ExtraArgs={"ContentType": content_type})
    s3.meta.client.put_object_tagging(
        Bucket=qr_code_bucket,
        Key=file_path,
        Tagging={
            'TagSet': [
                {
                    'Key': 'public',
                    'Value': 'yes'
                },
            ]
        }
    )

    response_body = {
        "url": url
    }

    response = {
        "isBase64Encoded": False,
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_body),
    }

    logger.info(response)
    return response
