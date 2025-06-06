from ..helpers.api import build_failure_response, build_success_response, assert_query_string_parameters
from ..helpers.mapping.subsite import __get_db_subsites_items, _post_subsite_in_db
from ..helpers.mapping.mapping import post_mapping, get_mapping
from decimal import Decimal
from typing import Dict, Any
import logging
import json
from ..app_config import AppConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def on_get_full_mapping(app_config_in: AppConfig, event_in, context, db_table_in):
    logger.info(f"getting full mapping for {event_in['queryStringParameters']}")
    # try:
        # assert_query_string_parameters(event_in, ["sample_id","id"])
    if 'queryStringParameters' not in event_in:
        return build_failure_response("queryStringParameters not defined")

    if 'sample_id' not in event_in['queryStringParameters']:
        return build_failure_response("sample_id not defined in queryStringParameters")
    
    if 'id' not in event_in['queryStringParameters']:
        return build_failure_response("id not defined in queryStringParameters") 
    
    mapping = get_mapping(
        app_config_in,
        db_table_in,
        event_in["queryStringParameters"]["sample_id"],
        event_in["queryStringParameters"]["id"])
    return build_success_response(mapping)
    # except KeyError as e:
    #     return build_failure_response(e.args)

def on_get_mapping_info(app_config_in: AppConfig, event_in, context, db_table):
    return None

def on_get_mapping_info_by_measurement_id(app_config_in: AppConfig, event_in, context, db_table_in):
    if 'queryStringParameters' not in event_in:
        return build_failure_response("queryStringParameters not defined")

    if 'sample_id' not in event_in['queryStringParameters']:
        return build_failure_response("sample_id not defined in queryStringParameters")
    
    if 'measurement_id' not in event_in['queryStringParameters']:
        return build_failure_response("measurement_id not defined in queryStringParameters")
    
    product_id = event_in['queryStringParameters']['measurement_id']
    sample_id = event_in['queryStringParameters']['sample_id']
    result = None # __get_db_map_items_by_measurement_id(db_table_in, sample_id, measurement_id)
    return build_success_response(result["Items"])

def on_get_mapping_site_data(app_config_in: AppConfig, event_in, context, db_table):
    if 'queryStringParameters' not in event_in:
        return build_failure_response("queryStringParameters not defined")
    
    if 'product_id' not in event_in['queryStringParameters']:
        return build_failure_response("product_id not defined in queryStringParameters")
    
    if 'sample_id' not in event_in['queryStringParameters']:
        return build_failure_response("sample_id not defined in queryStringParameters")
    
    if 'site_id' not in event_in['queryStringParameters']:
        return build_failure_response("site_id not defined in queryStringParameters")

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

def on_get_mapping_subsite_data(app_config_in: AppConfig, event_in, context, db_table_in):
    parent_id = event_in['queryStringParameters']['parent_id']
    sample_id = event_in['queryStringParameters']['sample_id']
    result = __get_db_subsites_items(db_table_in,sample_id, parent_id)
    return build_success_response(result["Items"])

def on_post_mapping_subsite_data(app_config_in: AppConfig, event_in, context, db_table_in):
    query_string_parameters = event_in['queryStringParameters']
    subsite_data = json.loads(event_in['body'], parse_float=Decimal, parse_int=int)
    result = _post_subsite_in_db(
        app_config_in = app_config_in,
        db_table_in = db_table_in,
        parent_id_in=query_string_parameters['parent_id'],
        sample_id_in=query_string_parameters['sample_id'],
        measurement_id_in=query_string_parameters['measurement_id'],
        product_id_in=query_string_parameters['product_id'],
        site_x_in=query_string_parameters['site_x'],
        site_y_in=query_string_parameters['site_y'],
        api_subsite_in=subsite_data)
    return build_success_response(result)

def on_get_mapping_by_sample(app_config_in: AppConfig, event_in, context, db_table):
    return None

def on_post_mapping_site_data(app_config_in: AppConfig, event_in, context, db_table):
    return None


def on_post_mapping_data(app_config_in: AppConfig, event_in, context, db_table_in):
    logger.info(f"posting mapping data")
    api_mapping = json.loads(event_in['body'], parse_float=Decimal)
    
    expected_keys = ["SampleId", "ProductId", "MeasurementId", "Content"]
    
    key_extra_errors = [ f"unexpected key '{key}' in posted item" for key in api_mapping if key not in expected_keys]
    key_missing_errors = [ f"missing key '{key}' in posted item" for key in expected_keys if key not in api_mapping ]
    
    if key_missing_errors or key_extra_errors:
        raise KeyError( ", ".join(key_missing_errors + key_extra_errors))
        
    api_mapping["DataType"] = "MappingData"
    api_mapping["ParentId"] = "None"
    api_mapping["SubsampleId"] = "None"
    mapping_id = post_mapping(app_config_in, db_table_in, api_mapping)
    return build_success_response(f"successfully posted mapping with id {mapping_id}")