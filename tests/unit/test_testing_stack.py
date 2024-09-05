import aws_cdk as core
import aws_cdk.assertions as assertions

from infra.iowaabd_tracking_stack import TestingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in infra/iowaabd_tracking_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TestingStack(app, "infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
