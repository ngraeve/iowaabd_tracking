import os

from aws_cdk import (
    Duration,
    Stack,
    aws_logs as _logs,
    aws_lambda as _lambda,
    aws_ssm as _ssm,
    aws_sns as _sns,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
)

from aws_cdk.aws_lambda_python_alpha import PythonFunction as _lambda_python
from constructs import Construct


class IowaabdTrackingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        sms_lottery_current_list_topic = _sns.Topic(
            self,
            'LotteryCurrentListTopic'
        )

        # sms_lottery_current_list_topic.add_subscription(
        #     _sns_subscriptions.SmsSubscription(os.environ['NICK_PHONE_NUMBER'])
        # )

        lottery_current_list_parameter = _ssm.StringParameter(
            self,
            "LotteryCurrentListParameter",
            parameter_name='/lottery/current',
            string_value='{}',
            description='Contains current list of lottery liquor from Iowaabd',
        )

        lottery_url_parameter = _ssm.StringParameter(
            self,
            "LotteryURLParameter",
            parameter_name='/lottery/iowaabd_url',
            string_value='https://shop.iowaabd.com/snapshot/lottery',
            description='Contains current list of lottery liquor from Iowaabd',
        )

        lottery_log_group = _logs.LogGroup(
            self,
            "Lottery Log Group",
            retention=_logs.RetentionDays.ONE_DAY,
            )

        lottery_function = _lambda_python(
            self,
            "LotteryFunction",
            entry="src/lambdas/lottery",
            runtime=_lambda.Runtime.PYTHON_3_12,
            index="lottery.py",
            handler="lambda_handler",
            log_group=lottery_log_group,
            timeout=Duration.seconds(20),
            environment={
                'lottery_current_list_parameter_name': lottery_current_list_parameter.parameter_name,
                'lottery_url_parameter_name': lottery_url_parameter.parameter_name,
                'sms_lottery_current_list_topic_arn': sms_lottery_current_list_topic.topic_arn
            },
        )

        lottery_function.role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMFullAccess'))
        sms_lottery_current_list_topic.grant_publish(lottery_function.role)

        cron_every_30_minutes = _events.Rule(
            self,
            'Every30Minutes',
            schedule=_events.Schedule.cron(minute='30'),
        )

        cron_every_30_minutes.add_target(_targets.LambdaFunction(lottery_function))
