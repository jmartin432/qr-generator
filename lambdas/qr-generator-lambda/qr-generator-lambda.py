import segno
import json
import logging
import os
import boto3
from string import Template
from urllib import parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

qr_code_bucket = os.environ['QRCodeBucketName']


def handler(event, context):
    logger.info('Received event: {event}'.format(event=json.dumps(event)))
    stage = event['requestContext']['stage']
    request_body = json.loads(event['body'])
    qr_code_name = 'new-code' if 'qr-code-name' not in request_body else request_body['qr-code-name']
    file_type = 'png' if 'file-type' not in request_body else request_body['file-type']
    data = 'www.justinlmartin.com' if 'data' not in request_body else request_body['data']
    scale = 1 if 'scale' not in request_body else request_body['scale']
    micro = False if 'micro' not in request_body else request_body['micro']
    dark = 'black' if 'dark' not in request_body else request_body['dark']
    light = 'white' if 'light' not in request_body else request_body['light']
    border = 4 if 'border' not in request_body else request_body['border']
    file_name = Template('$name.$extension').safe_substitute(name=qr_code_name, extension=file_type)
    file_key = Template('$stage/$name').safe_substitute(stage=stage, name=file_name)
    temp_file = Template('/tmp/$name').safe_substitute(name=file_name)
    content_type = Template('image/$type').safe_substitute(type=file_type)
    url = Template('https://$bucketName.s3.amazonaws.com/$path').safe_substitute(bucketName=qr_code_bucket,
                                                                                 path=file_key)

    qr_code = segno.make(data, micro=micro)
    qr_code.save(temp_file, scale=scale, dark=dark, light=light, border=border)

    tags = {
        "public": "yes"
    }

    extra_args = {
        "ContentType": content_type,
        "Metadata": {
            "data": data,
            "scale": str(scale),
            "micro": str(micro),
            "dark": dark,
            "light": light,
            "border": str(border)
        },
        "Tagging": parse.urlencode(tags)
    }

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(temp_file, qr_code_bucket, file_key, ExtraArgs=extra_args)

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

    logger.info('Response: {response}'.format(response=json.dumps(response)))
    return response
