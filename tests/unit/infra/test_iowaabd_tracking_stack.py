import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template, Match
from infra.iowaabd_tracking_stack import IowaabdTrackingStack


@pytest.fixture
def template():
    app = App()
    stack = IowaabdTrackingStack(app, "TestStack")
    return Template.from_stack(stack)


def test_sns_topic_created(template):
    template.has_resource_properties("AWS::SNS::Topic", {})


def test_ssm_parameter_created(template):
    template.has_resource_properties("AWS::SSM::Parameter", {
        "Name": "/lottery/current",
        "Description": "Contains current list of lottery liquor from Iowaabd",
        "Type": "String"
    })

    template.has_resource_properties("AWS::SSM::Parameter", {
        "Name": "/lottery/iowaabd_url",
        "Description": "Contains current list of lottery liquor from Iowaabd",
        "Type": "String"
    })


def test_lambda_function_created(template):
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "lottery.lambda_handler",
        "Runtime": "python3.12",
        "Timeout": 20
    })


def test_lambda_environment_variables(template):
    template.has_resource_properties("AWS::Lambda::Function", {
        "Environment": {
            "Variables": {
                "lottery_current_list_parameter_name": "/lottery/current",
                "lottery_url_parameter_name": "/lottery/iowaabd_url",
                "sms_lottery_current_list_topic_arn": {"Ref": Match.any_value()}
            }
        }
    })


def test_cloudwatch_log_group_created(template):
    template.has_resource_properties("AWS::Logs::LogGroup", {
        "RetentionInDays": 1
    })


def test_event_rule_created(template):
    template.has_resource_properties("AWS::Events::Rule", {
        "ScheduleExpression": "cron(30 * * * ? *)"
    })


def test_iam_permissions(template):
    template.has_resource("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": Match.array_with([{
                "Action": "ssm:*",
                "Effect": "Allow",
                "Resource": "*"
            }])
        }
    })

    template.has_resource_properties("AWS::SNS::TopicPolicy", {
        "Topics": [{"Ref": Match.any_value()}]
    })
