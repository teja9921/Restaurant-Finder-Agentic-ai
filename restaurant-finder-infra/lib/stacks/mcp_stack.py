"""CDK Stack for MCP Lambda and AgentCore Gateway integration."""
import json
from pathlib import Path

from aws_cdk import (
    Stack, 
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    CfnOutput
)
from constructs import Construct


class MCPStack(Stack):
    """Stack for MCP Lambda functions and Agentcore Gateway."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import existing secret instead of creating a new SearchAPI key
        searchapi_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "SearchAPISecret",
            secret_name="restaurant-finder/searchapi-key",
        )

        # Create Lambda execution role
        lambda_role = iam.Role(
            self, "MCPLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )

        # Grant secret read access to Lambda
        searchapi_secret.grant_read(lambda_role)

        # Load tool schema
        tools_schema_path = Path(__file__).parent.parent.parent / "mcp" /"lambda" / "tools_schema.json"
        with open(tools_schema_path) as f:
            tools_schema = json.load(f)

        # Create explicit log group for Lambda (replaces deprecated log_retention)
        mcp_lambda_log_group = logs.LogGroup(
            self,
            "RestaurantSearchLambdaLogGroup",
            log_group_name="/aws/lambda/restaurant-finder-mcp",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Create Lambda function
        mcp_lambda = lambda_.Function(
            self, "RestaurantSearchLambda",
            function_name="restaurant-finder-mcp",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("mcp/lambda"),
            timeout=Duration.seconds(30),
            memory_size=256,
            role=lambda_role,
            environment={
                "SEARCHAPI_SECRET_ARN": searchapi_secret.secret_arn,
                "TOOLS_SCHEMA": json.dumps(tools_schema),
                "LOG_LEVEL": "INFO"
            },
            log_group=mcp_lambda_log_group
        )


        # Grant Lambda permission to be invoked by Bedrock AgentCore
        mcp_lambda.grant_invoke(
            iam.ServicePrincipal("bedrock.amazonaws.com")
        )

        # Outputs
        CfnOutput(
            self, "LambdaArn",
            value=mcp_lambda.function_arn,
            description="Lambda ARN for AgentCore Gateway registration"
        )

        CfnOutput(
            self, "SearchAPISecretArn",
            value=searchapi_secret.secret_arn,
            description="Secret ARN for SearchAPI key"
        )
        