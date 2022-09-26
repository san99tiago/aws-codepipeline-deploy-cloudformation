from aws_cdk import (
    Stack,
    SecretValue,
    aws_iam,
    aws_ssm,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_codebuild,
    CfnCapabilities,
)
from constructs import Construct

class CdkPipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name_prefix: str,
        deployment_environment: str,
        main_resources_name: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load parameters to class attributes
        self.construct_id = construct_id
        self.name_prefix = name_prefix
        self.deployment_environment = deployment_environment
        self.main_resources_name = main_resources_name


        # Extra general variables
        self.main_stack_name = "{}-main-stack-{}".format(self.main_resources_name, self.deployment_environment)
        self.github_oauth_token = SecretValue.secrets_manager(
            "my-github-token",
            json_field="token",
        )

        # Main pipeline creation
        self.create_ssm_parameters_for_pipeline_vars()
        self.create_pipeline_role()
        self.create_pipeline()
        self.add_source_stage_to_pipeline()
        self.add_build_stage_to_pipeline()
        self.add_deploy_stage_to_pipeline()
        self.add_destroy_stage_to_pipeline()


    def create_ssm_parameters_for_pipeline_vars(self):
        description_for_all_params = "Parameter for {} solution in {} environment".format(self.main_resources_name, self.deployment_environment)
        self.ssm_parameter_main_resources_name = aws_ssm.StringParameter(
            self,
            id="{}-StringParameter1".format(self.construct_id),
            parameter_name="/{}/{}/main_resources_name".format(self.deployment_environment, self.main_resources_name),
            string_value=self.main_resources_name,
            description=description_for_all_params,
        )
        self.ssm_parameter_environment = aws_ssm.StringParameter(
            self,
            id="{}-StringParameter2".format(self.construct_id),
            parameter_name="/{}/{}/environment".format(self.deployment_environment, self.main_resources_name),
            string_value=self.deployment_environment,
            description=description_for_all_params,
        )


    def create_pipeline_role(self):
        self.pipeline_role = aws_iam.Role(
            self,
            id="{}-Role".format(self.construct_id),
            role_name="{}{}-role".format(self.name_prefix, self.main_resources_name),
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("codepipeline.amazonaws.com"),
                aws_iam.ServicePrincipal("codebuild.amazonaws.com"),
                aws_iam.ServicePrincipal("cloudformation.amazonaws.com"),
            ),
            description="Role for codepipeline deployment for {} solution in {} environment".format(self.main_resources_name, self.deployment_environment)
        )
        self.pipeline_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))


    def create_pipeline(self):
        self.deploy_cloudformation_pipeline = aws_codepipeline.Pipeline(
            self,
            id="{}-Pipeline".format(self.construct_id),
            pipeline_name="{}{}-pipeline".format(self.name_prefix, self.main_resources_name),
            role=self.pipeline_role,
        )


    def add_source_stage_to_pipeline(self):
        self.source_artifact = aws_codepipeline.Artifact("SourceArtifact")
        source_stage = self.deploy_cloudformation_pipeline.add_stage(stage_name="SourceStage")
        source_stage.add_action(
            aws_codepipeline_actions.GitHubSourceAction(
                action_name="Source",
                oauth_token=self.github_oauth_token,
                owner="san99tiago",
                repo="aws-codepipeline-simple-cf",
                branch="main",
                output=self.source_artifact,
            )
        )


    def add_build_stage_to_pipeline(self):
        build_project = aws_codebuild.PipelineProject(
            self,
            id="{}-CodeBuildProject".format(self.construct_id),
            project_name="{}{}-project".format(self.name_prefix, self.main_resources_name),
            role=self.pipeline_role,
            build_spec=aws_codebuild.BuildSpec.from_object(
                {
                    "version": "0.2",
                    "phases": {
                        "build": {
                            "commands": [
                                "mkdir -p \"artifacts\"",
                                "CREATION_DATE=$(date)",
                                "# This approach is to remove the automatic mask from default retrieve method for SSM-Parameter-Store values (default method masks variables)",
                                "export MAIN_RESOURCES_NAME=$(aws ssm get-parameter --name {} --query \"Parameter.Value\" --output text)".format(self.ssm_parameter_main_resources_name.parameter_name),
                                "export ENVIRONMENT=$(aws ssm get-parameter --name {} --query \"Parameter.Value\" --output text)".format(self.ssm_parameter_environment.parameter_name),
                                "cp \"cloudformation/cloudformation.yml\" \"artifacts/cloudformation.yml\"",
                                "cp \"cloudformation/configuration.json\" \"artifacts/configuration.json\"",
                                "sed -e \"s/\${MAIN_RESOURCES_NAME}/$MAIN_RESOURCES_NAME/g\" \"artifacts/configuration.json\" > \"tmp.json\" && mv \"tmp.json\" \"artifacts/configuration.json\"",
                                "sed -e \"s/\${ENVIRONMENT}/$ENVIRONMENT/g\" \"artifacts/configuration.json\" > \"tmp.json\" && mv \"tmp.json\" \"artifacts/configuration.json\"",
                                "sed -e \"s/\${CREATION_DATE}/$CREATION_DATE/g\" \"artifacts/configuration.json\" > \"tmp.json\" && mv \"tmp.json\" \"artifacts/configuration.json\"",
                                "echo \"Final configuration.json file result is:\"",
                                "cat \"artifacts/configuration.json\"",
                            ]
                        }
                    },
                    "artifacts": {
                        "files": [
                            "artifacts/*",
                        ]
                    }
                }
            ),
            description="Build project for {} solution in {} environment".format(self.main_resources_name, self.deployment_environment),
        )

        self.build_artifact = aws_codepipeline.Artifact("ModifiedArtifact")
        build_stage = self.deploy_cloudformation_pipeline.add_stage(stage_name="BuildStage")
        build_stage.add_action(
            aws_codepipeline_actions.CodeBuildAction(
                action_name="Build",
                input=self.source_artifact,
                project=build_project,
                outputs=[self.build_artifact],
            )
        )

    def add_deploy_stage_to_pipeline(self):
        deploy_stage = self.deploy_cloudformation_pipeline.add_stage(stage_name="DeployStage")
        deploy_stage.add_action(
            aws_codepipeline_actions.CloudFormationCreateUpdateStackAction(
                action_name="Deploy",
                stack_name=self.main_stack_name,
                admin_permissions=True,
                cfn_capabilities=[CfnCapabilities.AUTO_EXPAND, CfnCapabilities.NAMED_IAM, CfnCapabilities.ANONYMOUS_IAM],
                template_path=self.build_artifact.at_path("artifacts/cloudformation.yml"),
                template_configuration=self.build_artifact.at_path("artifacts/configuration.json"),
                role=self.pipeline_role,
                deployment_role=self.pipeline_role,
            )
        )


    def add_destroy_stage_to_pipeline(self):
        destroy_stage = self.deploy_cloudformation_pipeline.add_stage(
            stage_name="DestroyStage",
            transition_to_enabled=False,
            transition_disabled_reason="Disabled by default, because it should only be triggered for Stack deletion!",
        )
        destroy_stage.add_action(
            aws_codepipeline_actions.ManualApprovalAction(
                action_name="DestroyInfrastructure",
                additional_information="DESTROY CLOUDFORMATION RESOURCES (WARNING, ONLY FOR CLEANING UP INFRASTRUCTURE)!",
                run_order=1,
            )
        )
        destroy_stage.add_action(
            aws_codepipeline_actions.CloudFormationDeleteStackAction(
                action_name="Destroy",
                stack_name=self.main_stack_name,
                admin_permissions=True,
                cfn_capabilities=[CfnCapabilities.AUTO_EXPAND, CfnCapabilities.NAMED_IAM, CfnCapabilities.ANONYMOUS_IAM],
                role=self.pipeline_role,
                deployment_role=self.pipeline_role,
                run_order=2,
            )
        )
