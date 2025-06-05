import boto3
import json
import logging
import os
import uuid
from decimal import Decimal
from .handlers.product import handler_get_product_list
from .helpers.api import build_failure_response, build_success_response
from .handlers.mapping import (
    on_get_mapping_info,
    on_get_mapping_info_by_measurement_id,
    on_get_full_mapping,
    on_post_mapping_data,
    on_get_mapping_site_data,
    on_post_mapping_site_data,
    on_get_mapping_subsite_data,
    on_post_mapping_subsite_data,
    on_get_mapping_by_sample,
)
from .encoders.custom_encoder import CustomEncoder
from codeguru_profiler_agent import with_lambda_profiler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_item(db_table, item_uuid: str):
    try:
        print("getting item with uuid: " + item_uuid)
        response = db_table.get_item(
            Key={
                'Id': item_uuid
            }
        )

        if 'Item' not in response:
            return build_failure_response('Item not found')

        return build_success_response(response['Item'])
    except:
        logger.exception("exception occurred while retrieving item in table")


def get_items(db_table):
    response = db_table.scan(Limit = 100)
    if 'Items' not in response:
        return build_failure_response('Item not found')

    return build_success_response(response)        


def post_item(db_table, item_in: str):
    logger.info(f"adding item : '{item_in}'")
    item = json.loads(item_in, parse_float=Decimal)
    expected_keys = ["SampleId", "MeasurementId", "ParentId", "SubsampleId", "DataType", "Content", "ProductId"]
    key_extra_errors = [ f"unexpected key '{key}' in posted item" for key in item if key not in expected_keys]
    key_missing_errors = [ f"missing key '{key}' in posted item" for key in expected_keys if key not in item ]
    if key_missing_errors or key_extra_errors:
        raise KeyError( ", ".join(key_missing_errors + key_extra_errors))
    
    if type(item["Content"]) is dict:
        item["Content"] = json.dumps(item["Content"], cls=CustomEncoder)
    
    item["Id"] = str(uuid.uuid4())
    return db_table.put_item(
        Item=item
    )


def on_get_data(app_config_in, event_in, context, db_table):
    if 'queryStringParameters' in event_in and 'id' in event_in['queryStringParameters']:
        return get_item(db_table, event_in['queryStringParameters']['id']) 
    else:
        return get_items(db_table)
    
def on_post_data(app_config_in, event_in, context, db_table):    
    result = post_item(db_table, event_in['body'])
    return build_success_response(result)


def _get_table():
    if os.getenv("AWS_SAM_LOCAL"):
        return boto3.resource(
            'dynamodb',
            endpoint_url="http://localhost:8000/"
        ).Table("SciData")
    else:
        db_table_name = os.environ.get("SCIDATA_TABLE_NAME", None)
        if not db_table_name:
            raise SystemError("DynamoDb SCIDATA_TABLE_NAME not defined in environement variables")  
        return boto3.resource('dynamodb').Table(db_table_name)


@with_lambda_profiler()
def lambda_handler(event_in, context_in):
    logging.getLogger('codeguru_profiler_agent').setLevel(logging.INFO)
    db_table = _get_table()

    app_config = {"subsite_separate_storage":False}
    
    data_handlers = {
        "/data" : {
            "GET" : on_get_data,
            "POST": on_post_data
        },
        "/data/mapping/info" : {
            "GET" : on_get_mapping_info,
        },
        "/data/mapping/info/measurement_id" : {
            "GET" : on_get_mapping_info_by_measurement_id,
        },
        "/data/mapping/full" : {
            "GET" : on_get_full_mapping,
            "POST": on_post_mapping_data
        },
        "/data/mapping/site" : {
            "GET" : on_get_mapping_site_data,
            "POST": on_post_mapping_site_data
        },
        "/data/mapping/subsite" : {
            "GET" : on_get_mapping_subsite_data,
            "POST" : on_post_mapping_subsite_data
        },
        "/data/mapping/sample" : {
            "GET" : on_get_mapping_by_sample
        },
        "/data/products/" : {
            "GET" : handler_get_product_list
        }
    }

    path = event_in['path']
    httpMethod = event_in['httpMethod']
    if path not in data_handlers:
        return build_failure_response(f"Unsupported path \"{path}\"")
        
    if httpMethod not in data_handlers[path]:
        return build_failure_response(f"Unsupported method \"{httpMethod}\" for path \"{path}\"")
        
    return data_handlers[path][httpMethod](app_config, event_in, context_in, db_table)