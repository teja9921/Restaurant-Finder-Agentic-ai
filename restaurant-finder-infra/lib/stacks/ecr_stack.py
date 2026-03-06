"""ECR Stack for container registry."""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput
)
from aws_cdk import aws_ecr as ecr
from constructs import Construct

class EcrStack(Stack):
    """Stack for ECR container registry"""
    def __init__(scope: Construct, construct_id: str, **kwargs) ->None:
        super().__init__(scope, construct_id, **kwargs)

        #ECR repository for agent container
        self.repository = ecr.Repository(
            self, "AgentRepository",
            repository_name="restaurant-finder-agent",
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True,
            image_scan_on_push=True,
        )

        #Output Repository URI
        CfnOutput(
            self, "RepositoryUri",
            value=self.repository.repository_uri,
            description="ECR Repository URI",
            export_name="RestaurantFinderUri"
        )