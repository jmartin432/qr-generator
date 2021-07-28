import segno
import json
import logging
import os
import boto3
from string import Template

logger = logging.getLogger()
logger.setLevel(logging.INFO)

qr_code_bucket = os.environ['QRCodeBucketName']
qr_code_bucket_url = os.environ['QRCodeBucketUrl']


def handler(event, context):
    logger.info(event)
    request_body = json.loads(event['body'])
    file_name = Template('$name.$extension').safe_substitute(name=request_body['qr-code-name'],
                                                             extension=request_body['file-type'])

    temp_file = Template('/tmp/$name').safe_substitute(name=file_name)

    qr_code = segno.make(request_body['data'], micro=request_body['micro'])
    qr_code.save(temp_file)

    url = Template('$base/$path').safe_substitute(base=qr_code_bucket_url, path=file_name)

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(temp_file, qr_code_bucket, file_name)

    response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'url': url
    }

    return response
