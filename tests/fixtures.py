import pytest
import os
import boto3
from moto import mock_aws

TABLE_NAME = "SCIDATA_TABLE"

@pytest.fixture
def lambda_environment():
    os.environ["SCIDATA_TABLE_NAME"] = TABLE_NAME


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test_key_id"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_access_key"
    os.environ["AWS_SECURITY_TOKEN"] = "test_security_token"
    os.environ["AWS_SESSION_TOKEN"] = "test_session_token"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def mock_dynamodb(aws_credentials):
    with mock_aws():
        db_connection = boto3.client("dynamodb")
        
        db_connection.create_table(
            AttributeDefinitions=[                
                {"AttributeName": "SampleId", "AttributeType": "S"},
                {"AttributeName": "Id", "AttributeType": "S"},
                {"AttributeName": "MeasurementId", "AttributeType": "S"},
                {"AttributeName": "SubsampleId", "AttributeType": "S"},
                {"AttributeName": "ParentId", "AttributeType": "S"},
            ],
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "SampleId", "KeyType": "HASH"},
                {"AttributeName": "Id", "KeyType": "RANGE"}
            ],
            LocalSecondaryIndexes=[
                {
                    "IndexName":"SubsampleIdx",
                    "KeySchema":[
                        {"AttributeName": "SampleId", "KeyType": "HASH"},
                        {"AttributeName": "SubsampleId", "KeyType": "RANGE"}
                    ],
                    "Projection": { "ProjectionType": "ALL"}
                },
                {
                    "IndexName":"MeasurementIdx",
                    "KeySchema":[
                        {"AttributeName": "SampleId", "KeyType": "HASH"},
                        {"AttributeName": "MeasurementId", "KeyType": "RANGE"}
                    ],
                    "Projection": { "ProjectionType": "ALL"}
                },
                {
                    "IndexName":"ParentIdx",
                    "KeySchema":[
                        {"AttributeName": "SampleId", "KeyType": "HASH"},
                        {"AttributeName": "ParentId", "KeyType": "RANGE"}
                    ],
                    "Projection": { "ProjectionType": "ALL"}
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield db_connection

