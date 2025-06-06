from typing import Dict, Any
import uuid
import logging
from ..helpers.api import build_failure_response, build_success_response
import uuid
from decimal import Decimal
from ..encoders.custom_encoder import CustomEncoder
import json
from ..app_config import AppConfig

logger = logging.getLogger()

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

def on_get_data(app_config_in: AppConfig, event_in, context, db_table):
    if 'queryStringParameters' in event_in and 'id' in event_in['queryStringParameters']:
        return get_item(db_table, event_in['queryStringParameters']['id']) 
    else:
        return get_items(db_table)
    
def on_post_data(app_config_in: AppConfig, event_in, context, db_table):    
    result = post_item(db_table, event_in['body'])
    return build_success_response(result)