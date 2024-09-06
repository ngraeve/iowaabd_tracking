from aws_cdk import (
    Duration,
    Stack,
    aws_logs as _logs,
    aws_lambda as _lambda,
    aws_ssm as _ssm,
)

from aws_cdk.aws_lambda_python_alpha import PythonFunction as _lambda_python
from constructs import Construct


class IowaabdTrackingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lottery_parameter = _ssm.StringParameter(
            self,
            "LotteryParameter",
            parameter_name='/lottery/current',
            string_value='{}',
            description='Contains current list of lottery liquor from Iowaabd',
        )

        lottery_log_group = _logs.LogGroup(
            self,
            "Lottery Log Group",
            retention=_logs.RetentionDays.ONE_DAY,
            )

        _lambda_python(self,
                       "LotteryFunction",
                       entry="src/lambda/lottery",
                       runtime=_lambda.Runtime.PYTHON_3_12,
                       index="lottery.py",
                       handler="lambda_handler",
                       log_group=lottery_log_group,
                       timeout=Duration.seconds(20),
                       environment={
                           'lottery_parameter_name': lottery_parameter.parameter_name
                       },
                       )


        lottery_function = _lambda.Function(
            self,
            "HelloWorldFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("src/lambda/lottery"),
            handler="lottery.lambda_handler",
            log_group=lottery_log_group,
            timeout=Duration.seconds(20),
            environment={
                'lottery_parameter_name': lottery_parameter.parameter_name
            },

        )
