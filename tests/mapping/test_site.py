from tests.fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.mapping.site import _post_api_site_to_db
from src.app import _get_table, lambda_handler
from decimal import Decimal


def test_post_site(lambda_environment, mock_dynamodb):
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

    _post_api_site_to_db(
        db_table,
        "test_post_site_1_product",
        "test_post_site_1_sample",
        0, 0, 2, 3,
        api_site_data)

    result = db_table.scan(
            ExpressionAttributeValues = {
                ":Product":{"S":"test_post_site_1_product"},
                ":Sample":f"test_post_site_1_sample",
            }
        )
    
    assert result["Count"] == 3
