#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_pipeline_stack import CdkPipelineStack
import global_configurations as global_configs

# Validate deployment environment
valid_deployment = global_configs.validate_correct_deployment_environment(global_configs.DEPLOYMENT_ENVIRONMENT)
if valid_deployment == False:
    raise Exception({"SantiCustomError": "Environment '{}' is not valid. Use 'Development' or 'Production'.".format(global_configs.DEPLOYMENT_ENVIRONMENT)})


app = cdk.App()
pipeline_stack = CdkPipelineStack(
    app,
    "{}-codepipeline-{}".format(global_configs.MAIN_RESOURCES_NAME, global_configs.DEPLOYMENT_ENVIRONMENT),
    name_prefix=global_configs.NAME_PREFIX,
    deployment_environment=global_configs.DEPLOYMENT_ENVIRONMENT,
    main_resources_name=global_configs.MAIN_RESOURCES_NAME,
    env={
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
        "region": "us-east-1"
    },
    description="CI/CD stack for {} solution in {} environment".format(global_configs.MAIN_RESOURCES_NAME, global_configs.DEPLOYMENT_ENVIRONMENT),
)
global_configs.add_tags_to_stack(pipeline_stack)
app.synth()
