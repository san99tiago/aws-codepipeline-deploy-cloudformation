# LINKS AND EXTRA RESEARCH

These are some extra links that could be useful for CodePipeline deployments.

## Get codepipeline template from already created pipeline

https://stackoverflow.com/a/46640153/13957271

Reverse engineer an already created AWS CodePipeline to get the template

```
aws codepipeline get-pipeline --name "<PIPELINE_NAME>"
```

<br>

## Template configuration file for cloudformation

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html#d0e10167

<br>

## Actual needed role for codepipeline that deploys cloudformation

https://stackoverflow.com/questions/44931792/in-aws-codepipeline-how-do-i-assign-a-proper-role-name-to-allow-a-stack-deploym

<br>

## Simple pipeline with test/prod stacks example

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-basic-walkthrough.html
