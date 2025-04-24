import boto3
import json
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def build_failure_response(err):
    return {
        'statusCode': '400',
        'body': err.message,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def build_success_response(result : dict):
    return {
        'statusCode': '200',
        'body': json.dumps(result,cls=CustomEncoder),
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
            return build_success_response(response['Item'])
        else:
            return build_failure_response(ValueError('Item not found'))
        
    except:
        logger.exception("exception occurred while retrieving item in table")


def get_items(db_table):
    response = db_table.scan(Limit = 100)
    if 'Items' in response:
        return build_success_response(response)
    else:
        return build_failure_response(ValueError('Item not found'))


def post_item(db_table, item):
    return db_table.put_item(
        Item=item
    )


def on_get(event, context, db_table):
    if 'queryStringParameters' in event and 'id' in event['queryStringParameters']:
        return get_item(db_table, event['queryStringParameters']['id']) 
    else:
        return get_items(db_table)
    
    
def on_post(event, context, db_table):
    result = post_item(db_table, event['body'])
    return build_failure_response(None, result)


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    db_table = dynamodb.Table('products')
    
    handlers = {
        "GET" : on_get,
        "POST": on_post
    }

    httpMethod = event['httpMethod']
    if httpMethod in handlers:
        return handlers[httpMethod](event, context, db_table)     
    else:
        return build_failure_response(ValueError('Unsupported method "{}"'.format(httpMethod)))
