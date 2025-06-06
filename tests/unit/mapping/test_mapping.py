from ..fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app.helpers.mapping.mapping import post_mapping, get_mapping
from src.app.app import _get_table
from decimal import Decimal
import json
from boto3.dynamodb.conditions import Key
from src.app.app_config import AppConfig


def test_post_mapping(lambda_environment, mock_dynamodb):
    app_config = AppConfig(False, "dict")
    with open("test_data/test_post_mapping.json") as f:
        api_site_data = json.loads(f.read(), parse_float=Decimal, parse_int=int)
        api_site_data["ProductId"] = "test_post_mapping_1_product"
        api_site_data["SampleId"] = "test_post_mapping_1_sample"
        api_site_data["MeasurementId"] = "test_post_mapping_1_measurement" 

        db_table = _get_table()
        post_mapping(app_config, db_table, api_site_data)

        result = db_table.query(
            KeyConditionExpression=Key('SampleId').eq(api_site_data["SampleId"]))
        
        assert result["Count"] == 101

def test_post_mapping_with_content_as_string(lambda_environment, mock_dynamodb):
    app_config = AppConfig(False, "string")
    with open("test_data/test_post_mapping.json") as f:
        api_site_data = json.loads(f.read(), parse_float=Decimal, parse_int=int)
        api_site_data["ProductId"] = "test_post_mapping_1_product"
        api_site_data["SampleId"] = "test_post_mapping_1_sample"
        api_site_data["MeasurementId"] = "test_post_mapping_1_measurement" 

        db_table = _get_table()
        post_mapping(app_config, db_table, api_site_data)

        result = db_table.query(
            KeyConditionExpression=Key('SampleId').eq(api_site_data["SampleId"]))
        
        assert result["Count"] == 101

def test_post_mapping_subsites_separate_storage(lambda_environment, mock_dynamodb):
    app_config = AppConfig(subsite_separate_storage=True, content_format="dict")
    id_prefix = "test_post_mapping_subsites_separate_storage"
    with open("test_data/test_post_mapping.json") as f:
        api_site_data = json.loads(f.read(), parse_float=Decimal, parse_int=int)
        api_site_data["ProductId"] = id_prefix + "_1_product"
        api_site_data["SampleId"] = id_prefix + "_1_sample"
        api_site_data["MeasurementId"] = id_prefix + "_1_measurement" 

        db_table = _get_table()
        post_mapping(app_config, db_table, api_site_data)

        result = db_table.query(
            KeyConditionExpression=Key('SampleId').eq(api_site_data["SampleId"]))
        
        assert result["Count"] == 1701


def test_get_mapping(lambda_environment, mock_dynamodb):
    app_config = AppConfig(subsite_separate_storage=False, content_format="dict")
    with open("test_data/test_post_mapping.json") as f:
        api_mapping_posted = json.loads(f.read(), parse_float=Decimal, parse_int=int)
        api_mapping_posted["ProductId"] = "test_get_mapping_1_product"
        api_mapping_posted["SampleId"] = "test_get_mapping_1_sample"
        api_mapping_posted["MeasurementId"] = "test_get_mapping_1_measurement" 

        db_table = _get_table()
        row_id = post_mapping( app_config, db_table, api_mapping_posted)

        api_mapping = get_mapping(app_config, db_table, api_mapping_posted["SampleId"], row_id)

        assert api_mapping['MeasurementId'] == api_mapping_posted["MeasurementId"]
        assert api_mapping['ProductId'] == api_mapping_posted["ProductId"]
        assert api_mapping["Content"]["sites"][0][0]["name"] == api_mapping_posted["Content"]["sites"][0][0]["name"]
        assert api_mapping["Content"]["sites"][9][9]["name"] == api_mapping_posted["Content"]["sites"][9][9]["name"]

def test_get_mapping_with_content_as_string(lambda_environment, mock_dynamodb):
    app_config = AppConfig(subsite_separate_storage=False, content_format="string")
    with open("test_data/test_post_mapping.json") as f:
        api_mapping_posted = json.loads(f.read(), parse_float=Decimal, parse_int=int)
        api_mapping_posted["ProductId"] = "test_get_mapping_1_product"
        api_mapping_posted["SampleId"] = "test_get_mapping_1_sample"
        api_mapping_posted["MeasurementId"] = "test_get_mapping_1_measurement" 

        db_table = _get_table()
        row_id = post_mapping( app_config, db_table, api_mapping_posted)

        api_mapping = get_mapping(app_config, db_table, api_mapping_posted["SampleId"], row_id)

        assert api_mapping['MeasurementId'] == api_mapping_posted["MeasurementId"]
        assert api_mapping['ProductId'] == api_mapping_posted["ProductId"]
        assert api_mapping["Content"]["sites"][0][0]["name"] == api_mapping_posted["Content"]["sites"][0][0]["name"]
        assert api_mapping["Content"]["sites"][9][9]["name"] == api_mapping_posted["Content"]["sites"][9][9]["name"]