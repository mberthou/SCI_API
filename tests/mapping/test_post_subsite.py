from tests.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app import lambda_handler
from src.mapping.site import _post_subsite_in_db, _convert_api_to_db_subsite, _convert_db_to_api_subsite
from src.app import _get_table, lambda_handler
import json


def test_convert_subsite():
    api_subsite_data = {
        "name" : "test_subsite",
        "Vf" : 3.2,
        "Ir" : 1.2e-6
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
    


def test_get_post_subsite  (lambda_environment, mock_dynamodb):
    api_subsite_data = {
        "name" : "subsite_post_test_subsite",
        "Vf" : "3.2",
        "Ir" : "1.2e-6"
    }  
    
    event = {
        "path" : "/data/mapping/subsite",
        "httpMethod" : "POST",
        "queryStringParameters" : {
            "sample" : "subsite_post_test_sample",
            "product" : "subsite_post_test_product",
            "site_x" : "5",
            "site_y" : "7",
        },
        "body" : json.dumps(api_subsite_data)
    }

    lambda_handler(event, None)

    # _post_subsite_in_db(
    #    db_table,
    #    "test_product",
    #    "test_sample",
    #    "4",
    #    "6",
    #    api_subsite_data)


