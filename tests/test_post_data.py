from fixtures import lambda_environment, mock_dynamodb, aws_credentials
from src.app import lambda_handler

def test_post_data(lambda_environment, mock_dynamodb):
    with open("tests/payloads/post_payload.json") as payload_file:
        event = {
            "path" : "/data",
            "httpMethod" : "POST",
            "body" : payload_file.read()
        }

        response = lambda_handler(event, None)
        assert response["statusCode"] == '200'

def test_post_mapping_data(lambda_environment, mock_dynamodb):
    with open("tests/payloads/mapping1_payload.json") as mapping1_payload_file:
        post_event = {
            "path" : "/data/mapping/full",
            "httpMethod" : "POST",
            "body" : f"{mapping1_payload_file.read()}"
        }

        post_response = lambda_handler(post_event, None)
        assert post_response["statusCode"] == '200', post_response["body"]

