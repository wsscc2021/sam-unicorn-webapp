import boto3
import json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

class ContentNotFound(Exception):
    def __init__(self,message):
        self.message = message

@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    try:
        deleteUnicorn(event['unicorn'])
        return {
            'statusCode': 200,
            'body': json.dumps(f"Deleted {event['unicorn']}")
        }
    except ContentNotFound as error:
        return {
            'statusCode': 404,
            'body': json.dumps(error.message)
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps("Internal server error")
        }

@xray_recorder.capture('deleteUnicorn')
def deleteUnicorn(unicornName):
    try:
        dynamodb = boto3.resource('dynamodb')
        unicorn_table = dynamodb.Table('unicorn')
        response = unicorn_table.delete_item(
            Key={
                'unicornName': unicornName
            },
            ReturnValues='ALL_OLD'
        )
        if ('Attributes' not in response): raise ContentNotFound("The unicorn does not exist")
    except Exception as error:
        print("lambda_handler(): ",error)
        raise error