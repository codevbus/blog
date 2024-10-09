---
title: "deploy a terraform remote state backend with cloudformation"
date: 2017-12-21
slug: "deploy-a-terraform-remote-state-backend-with-cloudformation"
author: Mike vanbuskirk
categories: 
  - How-To
tags:
  - aws
  - terraform
  - cloudformation
  - infrastructure as code
---

Defining your infrastructure as code has become an integral part of many successful DevOps
workflows. Terraform has become a key tool, which I often employ to define a variety of
infrastructure. Today I'm going to show you how to set up the basic backend infrastructure needed to
allow multiple engineers to collaborate on the same resources in AWS, using Terraform and
CloudFormation.

### Prerequisites
To complete the actions described in this tutorial, you'll need access to an AWS account in which
you have permissions to access and provision resources. If you haven't already, go ahead and get the
AWS Command Line utility installed: [Installation Guide](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) and configured: [Configuration Guide](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

**DISCLAIMER**: Any AWS resources you provision during the course of this tutorial may result in
charges being billed to your account. The author assumes no responsibility, legal or otherwise, for
charges incurred.

### What Are We Doing? Why?
Now that you have Terraform installed, you should be able to create, modify, and destroy AWS
resources. The problem is, this setup is really only good for local testing and development. When it
comes time to start deploying production infrastructure, and multiple engineers need to work against
the same resource stacks, there needs to be some way to ensure consistency, and to avoid overlapping
changes. Enter remote state locking and backends.

Take some time to read the official [Hashicorp documentation on
backends](https://www.terraform.io/docs/backends/index.html). It explains what a backend is, what it
does, and the benefits of employing one.

Today we're going to deploy a remote backend with AWS S3, and state locking via AWS DynamoDB.

### Getting Started With AWS
I've already created the basic CloudFormation template to get the infrastructure created. If you
want to take a shortcut to get up and running, simply click the "Launch Stack" button below and
populate your variables as needed.

[![Launch CloudFormation Stack](../img/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?/stacks/new?stackName=terraform-backend&templateURL=https://s3.us-east-2.amazonaws.com/sysengcooking-blog-cf-templates/tf-backend.yaml)

```yaml
Parameters:
  StateBucketName:
    Description: Name of the S3 bucket to place the Terraform state files in.
    Type: String
  LockTableName:
    Description: Name of the DynamoDB table to store state locks.
    Type: String

AWSTemplateFormatVersion: 2010-09-09
Resources:
  TerraformStateBucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      AccessControl: Private
      BucketName: !Ref StateBucketName
      VersioningConfiguration:
        Status: Enabled

  TerraformLockTable:
    Type: 'AWS::DynamoDB::Table'
    Properties:
      AttributeDefinitions:
        - AttributeName: LockID
          AttributeType: S
      KeySchema:
        - AttributeName: LockID
          KeyType: HASH
      ProvisionedThroughput:
        ReadCapacityUnits: 5
        WriteCapacityUnits: 5
      TableName: !Ref LockTableName

Outputs:
  StackName:
    Value: !Ref AWS::StackName
```

If you want to launch the stack manually using the AWS CLI, create a file in your working directory
called `backend.yaml` and copy the above code in to it. The following command will launch the stack.
You will need to provide your desired values for the bucket name and DynamoDB table:

```bash
aws cloudformation create-stack --stack-name terraform-backend
   --template-body file://backend.yaml
   --parameters ParameterKey=StateBucketName,ParameterValue=<your_bucket_name> ParameterKey=LockTableName,ParameterValue=<your_lock_table_name>
```

Now we can move on to configuring our Terraform infrastructure to utilize our new remote state backend.

### Configuring Terraform
If you've deployed any infrastructure with Terraform, you are likely familiar with the basic,
overall structure of a project. You have the binary installed on your local development system,
and a root folder for a given project, containing at least one, often several terraform files.
Information about the state of the infrastructure is stored locally on your machine.

This works well for quick, iterative development work, but presents obvious problems for
collaboration. Using the infrastructure we deployed earlier in the tutorial, we'll configure a basic
Terraform project to utilize remote state storage and locking. This will enable the ability to
collaborate safely, as well as provide a safety net if the infrastructure state becomes corrupted or
lost on the local workstation.

```hcl
provider "aws" {
  region = "<aws_region>"
}

terraform {
  backend "s3" {
    bucket         = "<bucket_name>"
    key            = "<folder/filename.tfstate>"
    region         = "<aws_region>"
    dynamodb_table = "<dynamo_table_name>"
    encrypt        = true
  }
}
```

Populate the bucket, region, and dynamodb_table variables with the bucket name and dynamodb table
name you chose earlier, as well as the AWS region you are operating out of.

### Utilizing The Backend
We'll test our new backend by running a plan against a very simplistic AWS resource in a new Terraform project.
The backend can be used for multiple Terraform projects/environments, so feel free to configure your
other projects as needed.

Copy the `backend.tf` file you created earlier to a new project directory. From inside the
directory, run the command:

```bash
$ terraform init
```

Your output should be similar to the following:

```text
$ terraform init

Initializing the backend...

Successfully configured the backend "s3"! Terraform will automatically
use this backend unless the backend configuration changes.

Initializing provider plugins...
- Checking for available provider plugins on https://releases.hashicorp.com...
- Downloading plugin for provider "aws" (1.6.0)...

The following providers do not have any version constraints in configuration,
    so the latest version was installed.

    To prevent automatic upgrades to new major versions that may contain breaking
    changes, it is recommended to add version = "..." constraints to the
    corresponding provider blocks in configuration, with the constraint strings
    suggested below.

    * provider.aws: version = "~> 1.6"

    Terraform has been successfully initialized!

    You may now begin working with Terraform. Try running "terraform plan" to see
    any changes that are required for your infrastructure. All Terraform commands
    should now work.

    If you ever set or change modules or backend configuration for Terraform,
    rerun this command to reinitialize your working directory. If you forget, other
    commands will detect it and remind you to do so if necessary.
```

You can see in the first steps of the output, Terraform initializes and configures the
backend. Note that you are required to have the S3 bucket and DynamoDB table already deployed and
configured with the correct permissions before Terraform can utilize it.

The backend can be tested simply by running `terraform plan` against a basic resource config. I used
an empty security group to validate:

```hcl
resource "aws_security_group" "main" {
  name = "test"
  description = "test sg"
  vpc_id      = <your_vpc_id>
}
```

Be sure to fill in the correct value for your VPC id. Run:

```bash
$ terraform plan
```

inside the working directory. The import output to validate will come at the beginning:

```text
Acquiring state lock. This may take a few moments...
```

and end:

```text
Releasing state lock. This may take a few moments...
```

This lets you know that Terraform is interacting correctly with the remote lock table and state file.

### Conclusion
After completing this tutorial successfully, you should have a Cloudformation-defined remote state and locking infrastructure for Terraform. This is a major step towards utilizing Terraform on a larger scale for your infrastructure deployments!
