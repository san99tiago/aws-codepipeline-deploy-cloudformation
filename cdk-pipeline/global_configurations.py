#!/usr/bin/env python3
import aws_cdk as cdk

# Build-in imports
import os
import json
import subprocess
import datetime

# Get deployment variables from env variable or default to development
try:
    DEPLOYMENT_ENVIRONMENT = os.getenv("ENVIRONMENT").lower()
    NAME_PREFIX = "{}-".format(DEPLOYMENT_ENVIRONMENT)
    MAIN_RESOURCES_NAME = os.getenv("MAIN_RESOURCES_NAME").lower()
except Exception as e:
    raise Exception(
        {
            "SantiCustomError": "Environment variables not defined. {}".format(e)
        }
    )


def add_tags_to_stack(stack):
    """
    Simple function to add custom tags to stack in a centralized (equal) approach.
    """

    # Obtain current datetime for timestamp record
    now = datetime.datetime.now()
    datetime_formatted = now.strftime("%Y-%m-%d")
    current_aws_role = get_current_role()

    cdk.Tags.of(stack).add("Application", MAIN_RESOURCES_NAME)
    cdk.Tags.of(stack).add("Environment", DEPLOYMENT_ENVIRONMENT)
    cdk.Tags.of(stack).add("Owner", "Santiago Garcia Arango")
    cdk.Tags.of(stack).add("Usage", "Custom CodePipeline for deploying {} in {} environment".format(MAIN_RESOURCES_NAME, DEPLOYMENT_ENVIRONMENT))
    cdk.Tags.of(stack).add("CreationDate", datetime_formatted)
    cdk.Tags.of(stack).add("CreatedBy", current_aws_role)
    cdk.Tags.of(stack).add("GitHubRepo", "https://github.com/san99tiago/aws-codepipeline-simple-cf")


def validate_correct_deployment_environment(environment):
    """
    Function that validates the deployment environment.
    :return: bool (False if error and True if Ok).
    """
    if environment == "development" or environment == "production":
        print("Environment for deployment is: {}".format(environment))
        return True
    else:
        print("The environment for the deployment is not valid (only allowed \"development\" or \"production\")")
        return False


def validate_environment_variable(env_var_name, env_var_value):
    """
    Function that validates the existence of given environment variable.
    :return: bool (False if error and True if Ok).
    """
    if env_var_value == "":
        print("The environment variable {} is not defined".format(env_var_name))
        return False
    return True


def get_current_role():
    """
    Function that executes an "aws sts get-caller-identity" call and queries 
    the current execution IAM identity (User, Role, ...).
    :return: ARN of current AWS identity.
    """
    result = subprocess.run(["aws", "sts", "get-caller-identity"], stdout=subprocess.PIPE)
    caller_json = json.loads(result.stdout.decode("utf-8"))
    return caller_json["Arn"]


# Only for local tests (wont' be executed at deployments)
if __name__ == "__main__":
    print(get_current_role())
