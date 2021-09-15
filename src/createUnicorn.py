import boto3
import json, time
from botocore.exceptions import ClientError
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

class Forbidden(Exception):
    def __init__(self,message):
        self.message = message

@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    try:
        response = createUnicorn(
            unicornName=event['unicorn'],
            intelligence=event['body']['intelligence'],
            strength=event['body']['strength'],
            luck=event['body']['luck']
        )
        return {
            'statusCode': 201,
            'body': json.dumps(f"Created {event['unicorn']}")
        }
    except KeyError as error:
        return {
            'statusCode': 400,
            'body': json.dumps(f"There is no {error}")
        }
    except Forbidden as error:
        return {
            'statusCode': 403,
            'body': json.dumps(error.message)
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps("Internal server error")
        }

@xray_recorder.capture('createUnicorn')
def createUnicorn(unicornName, intelligence, strength, luck):
    try:
        dynamodb = boto3.resource('dynamodb')
        unicorn_table = dynamodb.Table('unicorn')
        response = unicorn_table.put_item(
            Item={
                'unicornName': unicornName,
                'intelligence': intelligence,
                'strength': strength,
                'luck': luck,
                'expire': int(time.time() + 60*5)
            },
            ConditionExpression="attribute_not_exists(unicornName)"
        )
        return response
    except ClientError as error:
        print("createUnicorn(): %s" % error)
        if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise Forbidden("The unicorn does already exist")
        else:
            raise error
    except Exception as error:
        print("createUnicorn(): %s" % error)
        raise error
        