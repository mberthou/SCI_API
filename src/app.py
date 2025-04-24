import boto3
import json
import logging
import os
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_LAMBDA_DYNAMODB_RESOURCE = { "resource" : boto3.resource('dynamodb'), 
                              "table_name" : os.environ.get("DYNAMODB_TABLE_NAME","NONE") }

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res,cls=CustomEncoder),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def get_item(db_table, item_uuid):
    try:
        print("getting item with uuid: " + item_uuid)
        response = db_table.get_item(
            Key={
                'id': item_uuid
            }
        )
        if 'Item' in response:
            return respond(None, response['Item'])
        else:
            return respond(ValueError('Item not found'))
        
    except:
        logger.exception("exception occurred while retrieving item in table")


def get_items(db_table):
    response = db_table.scan(Limit = 100)
    if 'Items' in response:
        return respond(None, response)
    else:
        return respond(ValueError('Item not found'))


def post_item(db_table, item):
    return db_table.put_item(
        Item=item
    )

def lambda_handler(event, context):
    print(f'event {event}')
    print(f'context {context}')

    body = json.loads(event['body'])
    user_name = body.get('user_name', None)
    password = body.get('password', None)
    
    response = {
        'statusCode' : 200,
        'body' : f'hello {user_name} from lambda'
    }

    return response
    #print("Received event: " + json.dumps(event, indent=2))

    dynamodb = boto3.resource('dynamodb')
    pace_table = dynamodb.Table('products')
    httpMethod = event['httpMethod']
    if httpMethod == 'GET':
        if 'queryStringParameters' in event and 'id' in event['queryStringParameters']:
            return get_item(pace_table, event['queryStringParameters']['id']) 
        else:
            return get_items(pace_table)

    elif httpMethod == 'POST':
        result = post_item(pace_table, event['body'])
        return respond(None, result)
        
    else:
        return respond(ValueError('Unsupported method "{}"'.format(httpMethod)))
