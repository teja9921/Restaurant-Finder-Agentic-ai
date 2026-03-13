"""CDK app entry point."""
import os
import aws_cdk as cdk
from lib.stacks.ecr_stack import EcrStack
from lib.stacks.mcp_stack import MCPStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'ap-south-1'),
)

#ECR stack
ecr_stack = EcrStack(
    app, "RestaurantFinderEcr", 
    env=env
)

# MCP Stack
mcp_stack = MCPStack(
    app, "RestaurantFinderMCPStack", 
    env=env
)

app.synth()