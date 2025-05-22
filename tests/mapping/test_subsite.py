import decimal
from decimal import Decimal
from tests.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.mapping.subsite import (
    _post_subsite_in_db, 
    _convert_api_to_db_subsite, 
    _convert_db_to_api_subsite,
    __get_db_subsites_items)
from src.app import _get_table, lambda_handler
import json
from src.Encoders.custom_encoder import CustomEncoder
import uuid
from boto3.dynamodb.conditions import And, Attr, Key


def test_convert_subsite():
    api_subsite_data = {
        "name" : "test_subsite",
        "Vf" : Decimal("3.2"),
        "Ir" : Decimal("1.2e-6")
    }
    parent_id = str(uuid.uuid4())
    db_subsite_data = _convert_api_to_db_subsite(
        parent_id,
        "sample_test",
        str(uuid.uuid4()),
        "product_test",
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

    parent_id = str(uuid.uuid4())
    sample_id = "test_post_subsite_in_db_sample"
    product_id = "test_post_subsite_in_db_product"
    measurement_id=str(uuid.uuid4())
    _post_subsite_in_db(
        db_table_in = _get_table(),
        parent_id_in = parent_id,      
        sample_in= sample_id,
        measurement_id_in=measurement_id,
        product_in = product_id,
        site_x_in = "4",
        site_y_in = "6",
        api_subsite_in = api_subsite_data)
    
    result = _get_table().scan(
            FilterExpression = (
                Attr("SampleId").eq(sample_id) &
                Attr("MeasurementId").eq(measurement_id) &
                Attr("ProductId").eq(product_id) &
                Attr("DataType").eq("Subsite") &
                Attr("SubsampleId").eq(f"X4Y6_{api_subsite_data['name']}"))
        )
    
    assert result["Count"] == 1

def test_get_subsite(lambda_environment, mock_dynamodb):
    prefix = "test_get_subsite"
    api_subsite_data = {
        "name" : f"{prefix}_name",
        "Vf" : Decimal("3.2"),
        "Ir" : Decimal("1.2e-6")
    }

    parent_id = str(uuid.uuid4())
    sample_id = f"{prefix}_sample"
    product_id = f"{prefix}_product"
    measurement_id=str(uuid.uuid4())
    db_table = _get_table()
    _post_subsite_in_db(
        db_table_in = db_table,
        parent_id_in = parent_id,      
        sample_in= sample_id,
        measurement_id_in=measurement_id,
        product_in = product_id,
        site_x_in = "4",
        site_y_in = "6",
        api_subsite_in = api_subsite_data)
    
    db_subsites = __get_db_subsites_items(db_table, sample_id, parent_id)

    assert len(db_subsites) == 1


def test_post_subsite_event  (lambda_environment, mock_dynamodb):
    api_subsite_data = {
        "name" : "test_post_subsite_event_subsite",
        "Vf" : 3.2,
        "Ir" : 1.2e-6
    }  
    
    parent_id = str(uuid.uuid4())
    event = {
        "path" : "/data/mapping/subsite",
        "httpMethod" : "POST",
        "queryStringParameters" : {
            "parent_id" : parent_id,
            "sample_id" : "test_post_subsite_event_sample",
            "product_id" : "test_post_subsite_event_product",
            "measurement_id" : str(uuid.uuid4()),
            "site_x" : "5",
            "site_y" : "7",
        },
        "body" : json.dumps(api_subsite_data, cls=CustomEncoder)
    }

    lambda_handler(event, None)

    result = _get_table().scan(
            ExpressionAttributeValues = {
                ":ProductId":{"S":event["queryStringParameters"]["sample_id"]},
                ":SampleId":{"S",event["queryStringParameters"]["product_id"]},
                ":MeasurementId":{"S",event["queryStringParameters"]["measurement_id"]},
            }
        )
    
    assert result["Count"] == 1


