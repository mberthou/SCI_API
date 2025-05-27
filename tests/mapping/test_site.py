from queue import Empty
from mypy_boto3_dynamodb import DynamoDBClient
from tests.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app.helpers.mapping.site import _post_api_site_to_db, _get_api_sites_from_db
from src.app.app import _get_table
from decimal import Decimal
from boto3.dynamodb.conditions import And, Attr, Key
from functools import reduce
import deepdiff
import uuid


def test_post_site(lambda_environment: None, mock_dynamodb: DynamoDBClient):
    app_config = {"subsite_separate_storage":False}
    db_table = _get_table()
    api_site_data = {
        "name" : "test_post_site_1",
        "sel" : 0,
        "NOSubs" : 2,
        "subsites": [
            {
            "name" : "test_post_site_1_subsite_1",
            "Vf" : Decimal("3.21"),
            "Ir" : Decimal("1.21e-6")
            },
            {
            "name" : "test_post_site_1_subsite_2",
            "Vf" : Decimal("3.22"),
            "Ir" : Decimal("1.22e-6")
            }
        ]
    }

    prefix="test_post_site_1"
    parent_id = str(uuid.uuid4())
    product_id = f"{prefix}_product"
    sample_id = f"{prefix}_sample"
    measurement_id = str(uuid.uuid4())
    site_row_id = _post_api_site_to_db(
        app_config,
        db_table,
        parent_id,
        sample_id,
        measurement_id,
        product_id,
        0, 0, 2, 3,
        api_site_data)

    results = db_table.scan(
            FilterExpression = (
                Attr("SampleId").eq(sample_id) & 
                Attr("MeasurementId").eq(measurement_id) &
                Attr("DataType").eq("Site")))
    
    assert results["Count"] == 1

    results = db_table.scan(
            FilterExpression = reduce(And,
                [Attr("ParentId").eq(site_row_id),
                 Attr("SampleId").eq(sample_id),
                Attr("MeasurementId").eq(measurement_id),
                Attr("DataType").eq("Subsite")]))

    assert results["Count"] == (2 if app_config["subsite_separate_storage"] else 0)

    results = db_table.query(
        IndexName="SubsampleIdx",
        KeyConditionExpression=(
            Key("SampleId").eq(sample_id) & 
            Key("SubsampleId").eq("X2Y3"))
    )
    assert results["Count"] == 1


def test_get_site(lambda_environment: None, mock_dynamodb: DynamoDBClient):
    app_config = {"subsite_separate_storage":False}
    prefix = "test_get_site"
    db_table = _get_table()
    api_site_data = {
        "name" : prefix + "_1",
        "sel" : Decimal('0'),
        "NOSubs" : Decimal('2'),
        "subsites": [
            {
            "name" : prefix + "_1_subsite_1",
            "Vf" : Decimal("3.21"),
            "Ir" : Decimal("1.21e-6")
            },
            {
            "name" : prefix + "_1_subsite_2",
            "Vf" : Decimal("3.22"),
            "Ir" : Decimal("1.22e-6")
            }
        ]
    }

    parent_id = str(uuid.uuid4())
    product_id = prefix + "_1_product"
    sample_id = prefix + "_1_sample"
    measurement_id = str(uuid.uuid4())

    _post_api_site_to_db(
        app_config,
        db_table,
        parent_id,
        sample_id,
        measurement_id,
        product_id,
        0, 0, 8, 9,
        api_site_data)

    result = _get_api_sites_from_db(
        app_config,
        db_table,
        sample_id_in=sample_id,
        parent_row_id=parent_id)
    
    result[0].pop("SiteX")
    result[0].pop("SiteY")
    diff = deepdiff.DeepDiff(result[0], api_site_data, ignore_order=True)
    assert diff == {}, f"unexpected result from get:\n{diff}"