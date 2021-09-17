import boto3
import json, os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

class ContentNotFound(Exception):
    def __init__(self,message):
        self.message = message

@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    try:
        unicornName = event['pathParameters']['unicorn']
        body = json.loads(event['body'])
        if not isExistUnicorn(unicornName):
            raise ContentNotFound("The unicorn does not exist")
        response = updateUnicorn(
            unicornName=unicornName,
            intelligence=body['intelligence'],
            strength=body['strength'],
            luck=body['luck']
        )
        return {
            'statusCode': 200,
            'body': json.dumps("Updated %s" % unicornName)
        }
    except KeyError as error:
        return {
            'statusCode': 400,
            'body': json.dumps("Bad request, There is no %s" % error)
        }
    except ContentNotFound as error:
        return {
            'statusCode': 404,
            'body': json.dumps("Content not found, %s" % error.message)
        }
    except Exception as error:
        print("lambda_handler(): %s" % error)
        return {
            'statusCode': 500,
            'body': json.dumps("Internal server error")
        }

@xray_recorder.capture('isExistUnicorn')
def isExistUnicorn(unicornName):
    try:
        lambda_client = boto3.client('lambda')
        payload = {
            "unicorn": unicornName
        }
        response = lambda_client.invoke(
            FunctionName=os.environ['UNICORN_READ_FUNCTION'],
            InvocationType='RequestResponse',
            Payload=bytes(json.dumps(payload), encoding='utf8')
        )
        response_payload = json.loads(response['Payload'].read().decode("utf-8"))
        if response_payload['statusCode'] == 200:
            return True
        else:
            return False
    except Exception as error:
        print("lambda_handler(): ",error)
        raise error

@xray_recorder.capture('updateUnicorn')
def updateUnicorn(unicornName, intelligence, strength, luck):
    try:
        dynamodb = boto3.resource('dynamodb')
        unicorn_table = dynamodb.Table('unicorn')
        response = unicorn_table.update_item(
            Key={
                'unicornName': unicornName
            },
            AttributeUpdates={
                'intelligence': {
                    'Value': intelligence,
                    'Action': 'PUT'
                },
                'strength': {
                    'Value': strength,
                    'Action': 'PUT'
                },
                'luck': {
                    'Value': luck,
                    'Action': 'PUT'
                },
            },
            ReturnValues='UPDATED_NEW'
        )
        return response
    except Exception as error:
        print("updateUnicorn(): %s" % error)
        raise error