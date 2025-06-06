import boto3
import logging
import os

from .helpers.mapping import subsite
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
from .handlers.generic_sample import (
    on_get_data,
    on_post_data
)
from codeguru_profiler_agent import with_lambda_profiler
from .app_config import AppConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

    app_config = AppConfig(subsite_separate_storage=False,content_format="string")
    
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
        
    return data_handlers[path][httpMethod](app_config, event_in, context_in, _get_table())