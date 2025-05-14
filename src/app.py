from ctypes import ArgumentError
import boto3
import json
import logging
from .Encoders.custom_encoder import CustomEncoder
from os import environ
import os
import uuid
from decimal import Decimal

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

        if 'Item' not in response:
            return build_failure_response(ValueError('Item not found'))

        return build_success_response(response['Item'])        
    except:
        logger.exception("exception occurred while retrieving item in table")


def get_items(db_table):
    response = db_table.scan(Limit = 100)
    if 'Items' not in response:
        return build_failure_response(ValueError('Item not found'))

    return build_success_response(response)        


def post_item(db_table, item_in: str):
    logger.info(f"adding item : '{item_in}'")
    item = json.loads(item_in, parse_float=Decimal)
    expected_keys = ["Sample", "Data", "Product", "DataType"]
    key_extra_errors = [ f"unexpected key '{key}' in posted item" for key in item if key not in expected_keys]
    key_missing_errors = [ f"missing key '{key}' in posted item" for key in expected_keys if key not in item ]
    if key_missing_errors or key_extra_errors:
        raise KeyError( ", ".join(key_missing_errors + key_extra_errors))
    
    if type(item["Data"]) is dict:
        item["Data"] = json.dumps(item["Data"], cls=CustomEncoder)
    
    item["id"] = str(uuid.uuid4())
    return db_table.put_item(
        Item=item
    )

def post_mapping_item(db_table, item_in: str):
    logger.info(f"adding mapping item : '{item_in}'")
    item = json.loads(item_in, parse_float=Decimal)
    expected_keys = ["Sample", "Data", "Product"]
    key_extra_errors = [ f"unexpected key '{key}' in posted item" for key in item if key not in expected_keys]
    key_missing_errors = [ f"missing key '{key}' in posted item" for key in expected_keys if key not in item ]
    if key_missing_errors or key_extra_errors:
        raise KeyError( ", ".join(key_missing_errors + key_extra_errors))
    
    if type(item["Data"]) is dict:
        item["Data"] = json.dumps(item["Data"], cls = CustomEncoder)
    
    item["id"] = str(uuid.uuid4())
    item["DataType"] = "MappingData"
    return db_table.put_item(
        Item=item
    )


def on_get_data(event_in, context, db_table):
    if 'queryStringParameters' in event_in and 'id' in event_in['queryStringParameters']:
        return get_item(db_table, event_in['queryStringParameters']['id']) 
    else:
        return get_items(db_table)
    
def on_get_mapping_data(event_in, context, db_table):
    return None

def on_get_mapping_site_data(event_in, context, db_table):
    if 'queryStringParameters' not in event_in:
        return build_failure_response(ArgumentError("queryStringParameters not defined"))
    
    if 'product' not in event_in['queryStringParameters']:
        return build_failure_response(ArgumentError("product not defined in queryStringParameters"))
    
    if 'sample' not in event_in['queryStringParameters']:
        return build_failure_response(ArgumentError("sample not defined in queryStringParameters"))
    
    if 'site' not in event_in['queryStringParameters']:
        return build_failure_response(ArgumentError("site not defined in queryStringParameters"))

    product_id = event_in['queryStringParameters']['product']
    sample_id = event_in['queryStringParameters']['sample']
    site_id = event_in['queryStringParameters']['site']
    result = db_table.scan(
            ExpressionAttributeValues = {
                ":Product":{"S":f"{product_id}"},
                ":Sample":f"{sample_id}",
            }
        )
    
    return build_success_response(result["Items"])

from .mapping.site import _get_subsite_db_item, _post_subsite_in_db

def on_get_mapping_subsite_data(event_in, context, db_table_in):
    product_id = event_in['queryStringParameters']['product']
    sample_id = event_in['queryStringParameters']['sample']
    site_x = event_in['queryStringParameters']['site_x']
    site_y = event_in['queryStringParameters']['site_y']
    subsite_name = event_in['queryStringParameters']['subsite_name']
    result = _get_subsite_db_item(db_table_in, product_id, sample_id, site_x,site_y,subsite_name)
    return build_success_response(result["Items"])

def on_post_mapping_subsite_data(event_in, context, db_table_in):
    product_id = event_in['queryStringParameters']['product']
    sample_id = event_in['queryStringParameters']['sample']
    site_x = event_in['queryStringParameters']['site_x']
    site_y = event_in['queryStringParameters']['site_y']
    subsite_data = json.loads(event_in['body'], parse_float=Decimal)
    result = _post_subsite_in_db(db_table_in, product_id, sample_id, site_x, site_y, subsite_data)
    return build_success_response(result)

def on_post_mapping_site_data(event_in, context, db_table):
    return None

def on_get_mapping_by_product(event_in, context, db_table):
    if 'queryStringParameters' not in event_in or 'product' not in event_in['queryStringParameters']:
        return build_failure_response(ArgumentError("product not defined in queryStringParameters"))
    
    product_id = event_in['queryStringParameters']['product']
    result = db_table.scan(
            ExpressionAttributeValues={":Product":{"S":f"{product_id}"}}
        )
    
    return build_success_response(result["Items"])
    
    
def on_post_data(event_in, context, db_table):    
    result = post_item(db_table, event_in['body'])
    return build_success_response(result)

def on_post_mapping_data(event_in, context, db_table):    
    result = post_mapping_item(db_table, event_in['body'])
    return build_success_response(result)

def _get_table():
    if os.getenv("AWS_SAM_LOCAL"):
        return boto3.resource(
            'dynamodb',
            endpoint_url="http://localhost:8000/"
        ).Table("SciData")
    else:
        db_table_name = environ.get("SCIDATA_TABLE_NAME", None)
        if not db_table_name:
            raise SystemError("DynamoDb SCIDATA_TABLE_NAME not defined in environement variables")  
        return boto3.resource('dynamodb').Table(db_table_name)

def lambda_handler(event_in, context_in):
    db_table = _get_table()
    
    data_handlers = {
        "/data" : {
            "GET" : on_get_data,
            "POST": on_post_data
        },
        "/data/mapping" : {
            "GET" : on_get_mapping_data,
            "POST": on_post_mapping_data
        },
        "/data/mapping/site" : {
            "GET" : on_get_mapping_site_data,
            "POST": on_post_mapping_site_data
        },
        "/data/mapping/product" : {
            "GET" : on_get_mapping_by_product
        },
        "/data/mapping/subsite" : {
            "GET" : on_get_mapping_subsite_data,
            "POST" : on_post_mapping_subsite_data
        }
    }

    path = event_in['path']
    httpMethod = event_in['httpMethod']
    if path not in data_handlers:
        return build_failure_response(ValueError('Unsupported path "{}"'.format(path)))
        
    if httpMethod not in data_handlers[path]:
        return build_failure_response(ValueError(f"Unsupported method \"{httpMethod}\" for path \"{path}\""))
        
    return data_handlers[path][httpMethod](event_in, context_in, db_table)