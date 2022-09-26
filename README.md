# AWS-CODEPIPELINE-SIMPLE-CF

Simple project that illustrates how to create a CI/CD pipeline with native AWS services to be able to deploy simple cloudformation stacks in AWS.

## Initial Steps

Create GitHub OAuth token and store it in AWS Secrets Manager (must be done before CDK deployment)

Go to GitHub [Personal Access Tokens](https://github.com/settings/tokens), and create a token with needed permissions. <br>

After that, create a secret in AWS Secrets Manager, with the AWS Console or with the following AWS CLI command (remember to replace the `<TOKEN_VALUE_HERE>` to you OAuth GitHub token):

```bash
aws secretsmanager create-secret --name my-github-token --description "Personal GitHub Token for CodePipeline Access" --secret-string '{"token":"<TOKEN_VALUE_HERE>"}' --tags '[{"Key":"Environment","Value":"Production"},{"Key":"Owner","Value":"san99tiago"}]' --region us-east-1
```

## Prepare the variables for the initial CDK deployment

The AWS CodePipeline is created by an initial CDK deployment (after that, it's configured and ready to work in the long-run). That means that the first deployment must configure some variables. These variables are loaded in the [`global_configurations.py`](cdk-pipeline/global_configurations.py) script, but are defined as "ENVIRONMENT VARIABLES" on the terminal. <br>

To load these variables, please run the [`env_vars_script.sh`](env_vars_script.sh)

## Deploy CDK app (to generate the CI/CD pipeline)

This deployment must be done only once (after that, it's ready to go in the long-term for cloudformation changes). To deploy this CDK solution, you should follow the steps in [`important_commands.sh`](important_commands.sh). <br>

An example of some commands for the deployment, could be:

```bash
# Activate Python virtual environment
source .venv/bin/activate

export ENVIRONMENT="development"
export MAIN_RESOURCES_NAME="github-simple-s3"

cdk deploy
```

## Destroy CDK app (only when project CI/CD pipeline is not needed anymore)

An example of destroying the stack of the CI/CD pipeline could be:

```bash
# Activate Python virtual environment
source .venv/bin/activate

export ENVIRONMENT="development"
export MAIN_RESOURCES_NAME="github-simple-s3"

cdk destroy
```
