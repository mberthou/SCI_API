import decimal
from decimal import Decimal
from tests.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.mapping.subsite import _post_subsite_in_db, _convert_api_to_db_subsite, _convert_db_to_api_subsite
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
        db_table_in = _get_table(),
        product_in = "test_post_subsite_in_db_product",
        sample_in = "test_post_subsite_in_db_sample",
        site_x_in = "4",
        site_y_in = "6",
        api_subsite_in = api_subsite_data)
    
    result = _get_table().scan(
            ExpressionAttributeValues = {
                ":Product":{"S":"test_post_subsite_in_db_product"},
                ":Sample":{"S","test_post_subsite_in_db_sample"},
                ":name":{"S","test_post_subsite_in_db_subsite"}
            }
        )
    
    assert result["Count"] == 1


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

    result = _get_table().scan(
            ExpressionAttributeValues = {
                ":Product":{"S":"test_post_subsite_event_sample"},
                ":Sample":{"S","test_post_subsite_event_product"},
                ":name":{"S","test_post_subsite_event_subsite"}
            }
        )
    
    assert result["Count"] == 1


