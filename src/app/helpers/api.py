from typing import Dict, List
from ..encoders.custom_encoder import CustomEncoder
import json

def build_failure_response(error_message:str):    
    return {
        'statusCode': '400',
        'body': error_message,
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

"""
raises Keyerror if:
- queryStringParameters not defined
- queryStringParameters keys not similar to expected_keys_in
"""
def assert_query_string_parameters(event_in:Dict, expected_keys_in: List[str]):
    if 'queryStringParameters' not in event_in:
        raise KeyError("queryStringParameters not defined in event")
    
    key_extra_errors = [ 
        f"unexpected key '{key}' in posted item" 
        for key in event_in["queryStringParameters"] 
        if key not in expected_keys_in
    ]
    key_missing_errors = [ 
        f"missing key '{key}' in posted item" 
        for key in expected_keys_in 
        if key not in event_in["queryStringParameters"]
    ]
    
    if key_missing_errors or key_extra_errors:
        raise KeyError(", ".join(key_missing_errors + key_extra_errors))