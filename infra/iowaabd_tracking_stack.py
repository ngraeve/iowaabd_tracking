from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
)
from constructs import Construct


class IowaabdTrackingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello_world_function = _lambda.Function(
            self,
            "HelloWorldFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("src/lambda"),
            handler="lottery.handler",
        )
