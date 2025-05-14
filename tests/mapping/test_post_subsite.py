import decimal
from decimal import Decimal
from tests.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app import lambda_handler
from src.mapping.site import _post_subsite_in_db, _convert_api_to_db_subsite, _convert_db_to_api_subsite
from src.app import _get_table, lambda_handler
import json
from src.Encoders.custom_encoder import CustomEncoder


def test_convert_subsite():
    api_subsite_data = {
        "name" : "test_subsite",
        "Vf" : Decimal("3.2"),
        "Ir" : Decimal("1.2e-6")
    }

    db_subsite_data = _convert_api_to_db_subsite(
        "aaaaaa",
        "product_test",
        "sample_test",
        "5",
        "2",
        api_subsite_data)
    
    api_subsite_data_back = _convert_db_to_api_subsite(
        db_subsite_data
    )

    assert api_subsite_data == api_subsite_data_back
    
def test_post_subsite_in_db(lambda_environment, mock_dynamodb):
    api_subsite_data = {
        "name" : "test_post_subsite_in_db_subsite",
        "Vf" : Decimal("3.2"),
        "Ir" : Decimal("1.2e-6")
    }

    _post_subsite_in_db(
        _get_table(),
        "test_product",
        "test_sample",
        "4",
        "6",
        api_subsite_data)


def test_post_subsite_event  (lambda_environment, mock_dynamodb):
    api_subsite_data = {
        "name" : "test_post_subsite_event_subsite",
        "Vf" : 3.2,
        "Ir" : 1.2e-6
    }  
    
    event = {
        "path" : "/data/mapping/subsite",
        "httpMethod" : "POST",
        "queryStringParameters" : {
            "sample" : "test_post_subsite_event_sample",
            "product" : "test_post_subsite_event_product",
            "site_x" : "5",
            "site_y" : "7",
        },
        "body" : json.dumps(api_subsite_data, cls=CustomEncoder)
    }

    lambda_handler(event, None)


