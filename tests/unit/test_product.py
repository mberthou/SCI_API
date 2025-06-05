from src.app.helpers.product import get_all_products_and_samples
from tests.unit.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app.app import _get_table
from decimal import Decimal
from src.app.helpers.generic_sample import post_generic_sample_data
import os

subsite_separate_storage = False
os.chdir(os.path.dirname(__file__))

def test_get_products(lambda_environment, mock_dynamodb):
    app_config = {"subsite_separate_storage":False}
    with open("mapping/test_data/test_post_mapping.json") as f:
        db_table = _get_table()

        generic_sample_data_1 = {
            "SampleId" : "sample1",
            "ProductId" : "product1",
            "ParentId" : "None",
            "MeasurementId" : "measurement1",
            "SubsampleId" : "None",
            "DataType" : "GenericSample",
            "Content" : { "Vf" : Decimal('3.2'), "Ir" : Decimal('1e-6') }
        }
        post_generic_sample_data(app_config, db_table, generic_sample_data_1)

        generic_sample_data_2 = {
            "SampleId" : "sample2",
            "ProductId" : "product1",
            "ParentId" : "None",
            "MeasurementId" : "measurement1",
            "SubsampleId" : "None",
            "DataType" : "GenericSample",
            "Content" : { "Vf" : Decimal('3.2'), "Ir" : Decimal('1e-6') }
        }
        post_generic_sample_data(app_config, db_table, generic_sample_data_2)

        generic_sample_data_3 = {
            "SampleId" : "sample3",
            "ProductId" : "product2",
            "ParentId" : "None",
            "MeasurementId" : "measurement1",
            "SubsampleId" : "None",
            "DataType" : "GenericSample",
            "Content" : { "Vf" : Decimal('3.2'), "Ir" : Decimal('1e-6') }
        }
        post_generic_sample_data(app_config, db_table, generic_sample_data_3)

        generic_sample_data_4 = {
            "SampleId" : "sample3",
            "ProductId" : "product2",
            "ParentId" : "None",
            "MeasurementId" : "measurement1",
            "SubsampleId" : "None",
            "DataType" : "GenericSample",
            "Content" : { "Vf" : Decimal('3.2'), "Ir" : Decimal('1e-6') }
        }
        post_generic_sample_data(app_config, db_table, generic_sample_data_4)
        
        results = get_all_products_and_samples(db_table_in=db_table)

