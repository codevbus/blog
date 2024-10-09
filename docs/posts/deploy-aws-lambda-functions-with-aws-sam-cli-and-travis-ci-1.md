---
title: "deploy aws lambda functions with aws-sam-cli and travis-ci: part 1"
author: Mike Vanbuskirk
date: 2018-05-22
slug: "deploy-aws-lambda-functions-with-aws-sam-cli-and-travis-ci-1"
categories: 
  - how-to
tags:
  - aws
  - serverless
  - ci/cd
  - travis 
  - python
  - infrastructure as code
---

As serverless computing makes its way into the toolbox of more engineers and developers,
the need for streamlined development and deployment options grows in importance. This 2-part series will
share a basic workflow I've developed for developing and deploying serverless functions to AWS.

This workflow is going to employ the largely ubiquitous, free platforms offered by GitHub and
Travis-CI for version-control and CI, respectively, but it could be adapted to a wider variety of
VCS and CI/CD platforms.

This will be a 2-part article. The first part will end with us having a local development
environment with the aws-sam-cli tool, as well as a basic, working example of an AWS Lambda
function.

First, let's look at the prerequisites needed.

## Prerequisites
This series is going to assume some basic knowledge around topics like AWS, and serverless functions.
Ideally, the reader has a few AWS Lambda functions under their belt already, and
is looking for a more streamlined and automated way to deploy them.

It's also assumed there is some basic familiarity and experience with version control systems,
specifically Git/Github in this case.

This workflow was performed on a Macbook Pro running OSX 10.12(Sierra). Installation of tools for
different platforms such as Linux or Windows may vary slightly.

The tools and services you'll need are as follows:

* An [AWS](https://aws.amazon.com) account you have permission to programmatically deploy resources to
* An account on [GitHub.com](https://github.com)
* An account on [Travis-CI.org](https://travis-ci.org)
* The latest [Python 2.7](https://www.python.org/downloads/)
* [Docker CE](https://www.docker.com/community-edition#/download)
* An up-to-date install of the [aws-sam-cli tool](https://github.com/awslabs/aws-sam-cli)

Note that the aws-sam-cli tool, a key part of the workflow, requires local, valid AWS user
credentials. These are typically deployed to a workstation as part of the installation of the AWS
CLI tool. Go ahead and follow these instructions if you don't already have this set up:

* [Installation Guide](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
* [Configuration Guide](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)

If you're having trouble installing any of the tools mentioned, check the documentation or GitHub
issues for the given project. Feel free to post in the comments as well and I'll do my best to help
out.

**DISCLAIMER**: Any AWS resources you provision during the course of this tutorial may result in
charges being billed to your account. The author assumes no responsibility, legal or otherwise, for
charges incurred.

## What Are We Doing? Why?
I touched on it briefly in the introduction to the article: serverless computing is booming. It's
easy to see the attractiveness presented by the platform. No more managing servers, OS updates, and
firewall rules. Discrete, ephemeral, finite chunks of computing resources that can be activated on
demand. Why pay for a server instance to sit and run a script every 24 hours when a serverless
function can do the same for a fraction of the cost and maintenance overhead?

However, with new usage models comes new challenges. How do you develop and test locally? How do
make serverless development part of your CI/CD workflow?

The first question is easy: the engineers at AWS have developed a **great**
tool with [aws-sam-cli](https://github.com/awslabs/aws-sam-cli). It offers an incredibly streamlined
and easy to way to develop, test, and provision AWS Lambda functions. Provisioning of live resources occurs via SAM
and AWS CloudFormation.

What about the second part? What if you want to go a step further, and automate testing and
deployment of your functions? Enter [Travis-CI](https://travis-ci.org). If you're not familiar,
Travis-CI provides a free continuous integration and testing tool that is both powerful and easy to
use.

As I mentioned before, this is going to be a pretty simplistic workflow, but the basic concepts
demonstrated here could be ported to a variety of different VCS and CI/CD tools as needed.

For the serverless function, we'll be deploying some basic Python code that generates a list of active EC2
instances. I'll provide a link to the complete source code via GitHub if you want to use that as an
example, but feel free to port your own function code into this tutorial.

Let's get to creating our development environment and our function.

## Create a GitHub Repository
First thing's first: we'll need to create a GitHub repository to store our project code, as well as
for integration with Travis-CI. I've created my repo
[here](https://github.com/codevbus/get-active-ec2-instances).

If you've already got a GitHub and Travis-CI account set up, great! If not, don't worry just yet
about setting it up, we'll touch on that a little bit later.

## Create the Lambda Function
If you want to use the example Lambda function I created, download [this folder](https://github.com/codevbus/get-active-ec2-instances/tree/master/getinstances) to your working directory.

You can view the code inline below. The `__init__.py` file is empty and used to indicate to Python
that the directory contains packages.

```python
import boto3
import json
import datetime

client = boto3.client('ec2')

response = client.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running'
            ]
        }
    ],
    MaxResults=100
)

def get_id(instances):
    """
    returns a list of EC2 instances that are in the 'running'
    state, return object is a list of dicts
    """
    running_instances = []
    for instance in instances["Reservations"][0]["Instances"]:
        running_instances.append({'Instance ID': instance['InstanceId']})
    if not running_instances:
        print("No running instances detected!")
    else:
        return running_instances

def dt_converter(d):
    """
    converts datetime objects to string objects
    """
    if isinstance(d, datetime.datetime):
        return d.__str__()

def encoder(j):
    """
    dumps json objects to strings so any datetime objects
    can be converted to compatible strings before reloading
    as json again
    """
    return json.loads(json.dumps(j, default = dt_converter))

def my_handler(event, context):
    """
    lambda event handler that returns the list of instances
    """
    return encoder(get_id(response))
```

This is a very simplistic function, with no error handling. The main purpose here is to demonstrate the potential of
using CI/CD tools to streamline serverless development.

## Create the SAM template
The sam local toolkit requires a SAM template to be defined. The template is a YAML file that is
used to define certain aspects of how your serverless infrastructure will function.

Additional documentation on usage is available on the [aws-sam-cli repo](https://github.com/awslabs/aws-sam-cli#usage).

The file is available to download in the repo mentioned above. Code is also provided inline below:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Lists active EC2 instances
Resources:
  GetInstances:
    Type: AWS::Serverless::Function
    Properties:
      Handler: getinstances.getinstances.my_handler
      Timeout: 300
      Runtime: python3.6
```

AWS provides good documentation on the various components of a SAM template
[here](https://docs.aws.amazon.com/lambda/latest/dg/serverless_app.html). I'll cover the relevant
portions of the template below:

* `Resources:` - Top level designation of the "resources" we want to provision with the template. In this case, it's
simply a Lambda function.

* `GetInstances:` - The function name. This is referenced when using the `sam` tool to invoke the
function.

* `Type:` - The type of resource. In this case `AWS::Serverless::Function`.

* `Properties:` - Denotes subsequent property values for the current resource layer.

* `Handler:` - This is where the magic happens. The "Handler" property points to the actual module
containing the code of your function. Working from right to left:

    * `my_handler` - The name of the event handler in the code itself.
    * `getinstances` - Refers to the module/file `getinstances.py`.
    * `getinstances` - The left-most index, it refers to the folder the module code is contained in.

* `Timeout:` - An integer value, in seconds, that defines how long the function can wait before
a timeout occurs.

* `Runtime:` - Defines the runtime environment of the function code. In this case I've chosen
`python3.6`.

Next, we'll generate a sample event payload to trigger the Lambda function with.

## Generate a Sample Payload
In the case of AWS, Lambda functions are often triggered via some type of "event". A variety of
AWS services generate events that are valid for triggering a function. Event payloads are JSON data
structures that provide specific information about their origin and purpose.

The aws-sam-cli tool provides an [awesome feature](https://github.com/awslabs/aws-sam-cli#generate-sample-event-source-payloads)
that enables users to generate mock event payloads for local development and testing.

For the purposes of this article, we'll generate a mock event from Cloudwatch Scheduled Events.
These events function similar to the Linux cron system, and fire on pre-defined schedule values.

Run the following command in the working directory of your repo:

``` sam local generate-event schedule > event.json```

The output is saved in the `event.json` file, so that it can be re-used for function invocation as
needed.

At this point, this is what the folder structure of my project repo looks like:

```bash
get-active-ec2-instances
|-- README.md
|-- event.json
|-- getinstances
|   |-- __init__.py
|   `-- getinstances.py
`-- template.yaml
```

Your file or folder names may be slightly different, but at the very least you should have the
module code, a template file, and a mock event. If everything looks good, let's move on to testing
the Lambda function.

## Test The Lambda Function
My favorite feature of the sam tool is the ability to invoke functions locally. No more uploading
functions to AWS and testing them live to see if they work correctly.

Run the following command in the working directory of your repo:

``` sam local invoke "GetInstances" -e event.json ```

If this is your first invocation with this particular runtime, the tool will take some time to
download the Docker image from the remote repo. After the tool reports the request ID, and
invocation billing data, the output of your function will be provided(if it generates readable
output).

In this case, the sample code generates a list of active EC2 instances, which would appear like so:

```json
[{"Instance ID": "i-0123456789abcdef"}, {"Instance ID": "i-1011121314ghijklm"}...]
```

If the code does not detect any running instances, you will get this output instead:

`No running instances detected!`

If you encounter any errors, check the AWS documentation for common failure cases. I tend to find
that most of my errors stem from authentication/credential issues. Feel free to post in the comments
if you are struggling.

## What's Next
Now we've got a great local development environment set up for developing and deploying Serverless
functions to AWS. But we're not done.

In part 2, we're going to use the Travis-CI tool to create an integrated testing and deployment set
up for our Lambda function.

Stay tuned!
