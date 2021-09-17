import boto3
import json, decimal
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

class ContentNotFound(Exception):
    def __init__(self, message):
        self.message = message

@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    try:
        if 'unicorn' in event:
            result = getUnicorn(event['unicorn'])
        else:
            result = scanUnicorn()
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except ContentNotFound as error:
        return {
            'statusCode': 404,
            'body': json.dumps(f"Content not found: {error.message}")
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps("Internal server error")
        }

@xray_recorder.capture('scanUnicorn')
def scanUnicorn():
    try:
        dynamodb = boto3.resource('dynamodb')
        unicorn_table = dynamodb.Table('unicorn')
        response = unicorn_table.scan(
            Limit=123,
            ProjectionExpression='#unicornName',
            # FilterExpression='string',
            ExpressionAttributeNames={
                '#unicornName': 'unicornName'
            }
        )
        return [ unicorn['unicornName'] for unicorn in response['Items'] ]
    except Exception as error:
        print("readUnicornList(): %s" % error)
        raise error

@xray_recorder.capture('getUnicorn')
def getUnicorn(unicornName):
    try:
        dynamodb = boto3.resource('dynamodb')
        unicorn_table = dynamodb.Table('unicorn')
        response = unicorn_table.get_item(
            Key={
                'unicornName': unicornName
            },
            # ProjectionExpression='string',
            # ExpressionAttributeNames={
            #     'string': 'string'
            # }
        )
        if 'Item' not in response:
            raise ContentNotFound("The unicorn does not exist")
        else:
            return decimalToInteger(response['Item'])
    except Exception as error:
        print("readUnicornList(): %s" % error)
        raise error

@xray_recorder.capture('decimalToInteger')
def decimalToInteger(dictionary):
    try:
        for key,value in dictionary.items():
            if isinstance(value, decimal.Decimal):
                dictionary[key] = int(value)
        return dictionary
    except Exception as error:
        print("decimalToInteger(): %s" % error)
        raise error