from .fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app.helpers.mapping.mapping import post_mapping
from src.app.helpers.generic_sample import delete_all
from src.app.app import _get_table
from decimal import Decimal
import json
from boto3.dynamodb.conditions import Key
from src.app.app_config import AppConfig


def test_delete_all(lambda_environment, mock_dynamodb):
    app_config = AppConfig(subsite_separate_storage=False, content_format="string")
    with open("mapping/test_data/test_post_mapping.json") as f:
        db_table = _get_table()

        result = db_table.scan(ProjectionExpression="Id,SampleId")
        assert result['Count'] == 0

        api_site_data = json.loads(f.read(), parse_float=Decimal, parse_int=int)
        api_site_data["ProductId"] = "test_post_mapping_1_product"
        api_site_data["SampleId"] = "test_post_mapping_1_sample"
        api_site_data["MeasurementId"] = "test_post_mapping_1_measurement"        
        post_mapping(app_config, db_table, api_site_data)

        result = db_table.scan(ProjectionExpression="Id,SampleId")
        assert result['Count'] == 101

        delete_all(app_config, db_table)

        result = db_table.scan(ProjectionExpression="Id,SampleId")
        assert result['Count'] == 0


