import os
import json
import logging
import pytest
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError
from botocore.stub import Stubber

from src.lambdas.lottery.lottery import get_ssm_parameter_value, get_live_data, write_new_data, lambda_handler


@pytest.fixture
def mock_ssm_client():
    with mock_aws():
        yield boto3.client("ssm", region_name="us-east-1")

@pytest.fixture
def mock_ssm_parameter(mock_ssm_client):
    # Put a mock parameter into the SSM parameter store
    mock_ssm_client.put_parameter(
        Name="/test/parameter",
        Value="test_value",
        Type="String"
    )


def test_ssm_get_parameter_value_success(mock_ssm_client, mock_ssm_parameter, caplog):
    # Call the function that fetches the parameter
    result = get_ssm_parameter_value("/test/parameter")

    # Assert that the returned value is correct
    assert result == "test_value"
    assert "Response is test_value" in caplog.text


def test_ssm_get_parameter_value_not_found(mock_ssm_client, caplog):
    stubber = Stubber(mock_ssm_client)
    stubber.add_client_error('get_parameter', service_error_code='ParameterNotFound')
    stubber.activate()

    with caplog.at_level(logging.ERROR):
        result = get_ssm_parameter_value("/nonexistent/parameter")

        assert result is None
        # assert "Parameter /nonexistent/parameter not found" in caplog.text


def test_get_ssm_parameter_value_access_denied(mock_ssm_client, caplog):
    stubber = Stubber(mock_ssm_client)
    stubber.add_client_error('get_parameter', service_error_code='AccessDeniedException')
    stubber.activate()

    with caplog.at_level(logging.ERROR):
        result = get_ssm_parameter_value("/test/parameter")

        assert result is None
        # assert "Parameter /test/parameter not found" in caplog.text
        # assert "Access denied to parameter /test/parameter" in caplog.text
