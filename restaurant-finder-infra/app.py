"""CDK app entry point."""
import os
from aws_cdk import App, Environment
from lib.stacks.ecr_stack import EcrStack

app = App()

#environement configuration
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'ap-south-1'),
)

#ECR stack
ecr_stack = EcrStack(app, "RestaurantFinderEcr", env=env)

app.synth()