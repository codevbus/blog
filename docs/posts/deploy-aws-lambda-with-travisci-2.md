---
title: "deploy aws lambda functions with aws-sam-cli and travis-ci: part 2"
author: Mike Vanbuskirk
date: 2018-06-08
slug: "deploy-aws-lambda-functions-with-aws-sam-cli-and-travis-ci-2"
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

In part 1 of this series, we created a basic serverless function with AWS Lambda.
In part 2, we're going to use GitHub and Travis-CI to set up a continuous integration workflow.

If you completed [part 1](https://mikevanbuskirk.io/posts/deploy-aws-lambda-functions-with-aws-sam-cli-and-travis-ci-1/) successfully,
you should have a working AWS Lambda function. However, it's only exists locally on the machine it
was developed on. What if we want to deploy it to an AWS account? With an S3 bucket available, we
could simply use `sam package` and `sam deploy` to create a deployment package for, and deploy our
Lambda function to AWS.

Boom. Done.

That's not really sufficient for modern software/infrastructure deployment though, is it? Testing
and validation is(or at least should be) a critical part of any deployment. *How* a system will
function in a live environment should be determined *before* it ever hits that environment. It may
not be possible to 100% simulate every scenario, or validate every piece of logic, but modern tools
help us get close.

## Prerequisites
It's assumed that we've got all the prerequisites from part 1, as well as the working function ready
for deployment.

It will probably be helpful to have a quick read of the introductory Travis-CI docs:

* [Core Concepts For Beginners](https://docs.travis-ci.com/user/for-beginners) - Great intro on core
concepts of CI and Travis.
* [Getting Started Guide](https://docs.travis-ci.com/user/getting-started) - Getting started using
Travis.

It might also be helpful to install the Travis gem. If you don't have Ruby gems, start here:
<https://rubygems.org/>. You can then do `gem install travis` to have a local cli utility available
as needed as you work with Travis-CI.

Let's go ahead and get started.

## What Are We Doing? Why?(cont.)
Continuing the theme of part 1, we're setting up a CI testing and deployment workflow for serverless
functions using AWS Lambda, Github, and Travis-CI.

In part 2, we'll check in our code to the Github repo we've got set up. Then we're going to be setting
up a couple AWS resources for Travis-CI and sam to use for deployment. Finally, we'll get
everything configured and integrated together, so we've got an automated, CI deployment system!

## Commit The Code To Github
If you haven't already, you should commit your code to Github. You should already have a remote repo
configured.

Github provides an [excellent
tutorial](https://help.github.com/articles/adding-an-existing-project-to-github-using-the-command-line/)
for getting set up if you need guidance.

A key concept to remember(discussed in the Core Concepts documentation from Travis-CI) is that
continuous integration(CI) is based on small code changes and frequent code check-ins. In fact,
Travis-CI will run a build/deploy on *every* code check-in. This probably seems foreign, or even
scary to someone used to more traditional development and deployment methodologies, but fear not!
Once gotten used to, the paradigm of frequent deploys and frequent check-ins will become second
nature, and ultimately allows faster feedback and iteration on code changes.

Now we can move on to getting our AWS resources squared away so Travis-CI can run successful
deployments.

## Deploy Your AWS Resources
Before we can utilize Travis-CI to push our deployments, we need to setup three pieces of AWS
infrastructure.

Specifically, we'll be deploying an S3 bucket, an IAM user, and an IAM role. The S3 bucket will be used to upload
code artifacts to via aws-sam-cli. The IAM user will be utilized by Travis-CI to interact with
and create AWS resources, and the IAM role will be used by Lambda to query EC2 resources.

I'm a big proponent of infrastructure as code, and I'd generally reach for something like Terraform
or Cloudformation to deploy these resources. *However*, I want to keep this simple and focused on
the CI integration, so we'll deploy these resources manually via the AWS console.

Log in to your AWS account. Start with creating a basic S3 bucket with default options. Choose
a unique name and save it for later.

Next, we need to set up an IAM role. IAM roles are similar to IAM users, *except* they are
designed, generally, to be used/assumed by services and non-human entities. They are an incredibly
useful way to delegate permissions/access to your applications and services *without* having to
store traditional credentials.

In this specific case, the IAM role will be assumed by the AWS Lambda service so that your function
has the neccessary permissions to carry out whatever actions it needs to. The permissions that you
attach to the role will vary depending on the purpose of the function. If you're using the sample
function I've provided, then some basic "Read" permissions on EC2 resources will be suffice.

Go to the IAM console, and create a new role. Choose "Lambda" for the service. For the policy, AWS
actually provides an existing policy we can use. Choose "AmazonEC2ReadOnlyAccess". On the "Review"
screen, ensure everything looks correct. Give your a function a name that at least alludes to its
primary function. I named mine `ReadEC2StatusLambda`. Be sure to save the role ARN for later, as
you'll need it for the IAM user policy.

Finally, we need to create an IAM user that Travis-CI can utilize to integrate with AWS. From the
IAM console, you will need to navigate to "Users", where you view existing users, as well as create
a new one. Go ahead and hit the "Add User" button. Start by giving the user a meaningful name that
will make it easy to identify its purpose, like: `TravisServerlessDeploymentUser`. This will be a
"service account", so for "Access Type", we're only going to choose "programmatic access".

For permissions, choose "Attach existing policies directly", then hit the "Create policy" button.
Choose the "JSON" tab, and enter the following into the policy editor:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowListArtifactBucket",
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::<your-bucket-name-here>"
        },
        {
            "Sid": "AllowArtifactBucketUse",
            "Effect": "Allow",
            "Action": [
                "s3:PutObjectAcl",
                "s3:PutObject",
                "s3:GetObjectAcl",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::<your-bucket-name-here>/*"
        },
        {
            "Sid": "AllowLambdaAll",
            "Effect": "Allow",
            "Action": "lambda:*",
            "Resource": "*"
        },
        {
            "Sid": "AllowCloudFormationAll",
            "Effect": "Allow",
            "Action": "cloudformation:*",
            "Resource": "*"
        },
        {
          "Sid": "AllowIAMListPolicies",
          "Effect": "Allow",
          "Action": "iam:ListPolicies",
          "Resource": "*"
        },
        {
          "Sid": "AllowPassLambdaRole",
          "Effect": "Allow",
          "Action": "iam:PassRole",
          "Resource": "<your-role-arn-here>"
        }
    ]
}
```

Give the policy a meaningful name, similar to the IAM user you created previously. Be sure to
replace both instances of `<your-bucket-name-here>` with the name of the bucket you created
previously. You will also need to replace `<your-role-arn-here>` with the ARN of the role you
generated in the previous step.

Review the policy and save it. Afterwards you'll be returned to the user
creation process. Hit "refresh" on the policy list, and search for the policy you just
created. Select the policy, and proceed to "Review". If everything looks good, click "Create User".

On the next screen, you'll be shown the access key and secret key. **Make sure** you save these in
a safe place: this will be the **only** time you are shown them, and we'll need them for Travis-CI
integration.

Now we can move on to configuring our Travis-CI integration.

## Configure Travis-CI Integration
In Part 1 of this series, some basic prerequisites were laid out, including an account on both
GitHub and Travis-CI.

Signing in to Travis-CI with your GitHub account, via OAuth, should make all your repositories
available for Travis to integrate with.

Check the [Getting Started](https://docs.travis-ci.com/user/getting-started/) documentation if you
need help.

Once you get logged in to Travis-CI, you'll need to enable it for the specific respository you're
trying to integrate with. Under your "Profile", it will list all your public repositories. If you
want to integrate with private repositories, it requires a paid subscription on their .com site.
Once that's complete, you now have working Travis-CI integration!

The central component required for Travis-CI is the config file: `.travis-ci.yml`. This is a YAML
dotfile that provides a variety of configuration options, which tell Travis "how" to build your
software.

Rather than provide an exhaustive dive on every possible option(of which there are *many*), I'll
provide the basic file I used for this project, and explain the relevant bits. I highly suggest
taking the time to go through the official Travis-CI documentation to familiarize yourself with the
options available, as well as the high-level concepts of how it operates.

My configuration file is as follows:

```yaml
language: python
python:
- '2.7'
branches:
  only: master
install:
- pip install awscli
- pip install aws-sam-cli
script:
- sam validate
- sam package --template-file template.yaml --s3-bucket <your-bucket-name> --output-template-file packaged.yaml
deploy:
  provider: script
  script: sam deploy --template-file packaged.yaml --stack-name travis-serverless-test
  skip_cleanup: true
  on:
    branch: master
notifications:
  email:
    on_failure: always
env:
  global:
  - AWS_DEFAULT_REGION=us-east-2
  - secure: <obfuscated AWS Access Key>
  - secure: <obfuscated AWS Secret Key>
```

Let's take a walk through the configuration:

```yaml
language: python
```
The language setting specifies the build environment that Travis uses for the
project. Since we need to install `awscli` and `aws-sam-cli` via pip, Python is the natural choice.

```yaml
python:
- '2.7'
```
Defines what version of Python the project uses. In this case, due to a dependency with
`aws-sam-cli`, we need Python 2.

```yaml
branches:
  only: master
```
This setting ensures that builds are only triggered on commits to the "master" branch of the repo.

```yaml
install:
- pip install awscli
- pip install aws-sam-cli
```
The "install" is the step where we install the packages/dependencies needed for our build. In this
example, we use the Pip tool to install `awscli` and `aws-sam-cli`.

```yaml
script:
- sam validate
- sam package --template-file template.yaml --s3-bucket <your-bucket-name> --output-template-file packaged.yaml
```
The "script" block is where the default build steps can be overridden. In this case, we call the
`sam validate` command from the `aws-sam-cli` package to validate our SAM template, then `sam
package` to build our function into a deployable artifact. Note that `<your-bucket-name>` should be
replaced with the name of the S3 bucket that was created earlier in the tutorial. This is where the
packaged deployment artifact is stored. Also note the `--output-template-file packaged.yaml`. This
is a YAML file that will be utilized by the deployment step.

```yaml
deploy:
  provider: script
  script: sam deploy --template-file packaged.yaml --stack-name travis-serverless-test
  skip_cleanup: true
  on:
    branch: master
```
The "deploy" step is where we actually deploy our code to whatever provider we've
defined. Travis-CI supports many different providers
directly: <https://docs.travis-ci.com/user/deployment/#Supported-Providers>.

In this case we're using the generic `script` provider, which passes whatever build artifacts
we generated in our build step to custom scripts or commands. Our command is `sam deploy`, which
references the `packaged.yaml` artifact from the build step, as well as defines the name of the "stack".
I've chosen `travis-serverless-test`, but feel free to employ whatever naming scheme you choose.
This will actually be the name of a CloudFormation stack that the sam tool creates to deploy the
Lambda function. `skip_cleanup: true` prevents Travis-CI from deleting any changes made during the
build. `on: branch: master` ensures that deployments only occur on changes to the master branch.
A possible configuration would be to allow builds on all branches, but deploys only on "master".

```yaml
notifications:
  email:
    on_failure: always
```
Notifications defines how you are notified when things occur during the course of
a build/deployment. In this example I've configured it notify via email whenever there is a failure.

```yaml
env:
  global:
  - AWS_DEFAULT_REGION=<your-aws-region>
  - secure: <obfuscated AWS Access Key>
  - secure: <obfuscated AWS Secret Key>
```
The "env" block is where environment variables are defined. These are variables that can be made
available for any stage of the process. I highly recommend reading the official docs:
<https://docs.travis-ci.com/user/environment-variables/>. Environment variables are a critical
component of most CI systems, and familiarity with them will be a benefit going forward.

For this particular use case, we need 3 specific environment variables defined:

* `AWS_DEFAULT_REGION` - Defines which region we are deploying resources to, and is required by
the `aws-sam-cli` tool. I use `us-east-2`. You'll want to choose the nearest region that has the Lambda
and CloudFormation services available.

* `secure` - These are secure(encrypted) variables. In this particular case, we're using them to
store the credentials of the IAM user we created previously. Again, the Travis-CI documentation:
<https://docs.travis-ci.com/user/environment-variables/#Defining-encrypted-variables-in-.travis.yml>
provides a great resource to explain how.

In this case, I used the `travis` gem to add encrypted variables to my `.travis-ci.yml` file. If
you're worried about sensitive credentials being stored in your shell history, most shells will not
write a command to the hist file if you prepend them with a space.

You can also add the variables via the Travis-CI site, where they will be obfuscated. However they
will show up in the deployment log. I highly recommend using the gem method described above.

Now Travis-CI is configured, and we're ready to deploy our code.

## Deploy Your Function
Your project directory should look fairly similar to this(not counting `.git*` files):

```
get-active-ec2-instances
|-- .travis.yml
|-- README.md
|-- event.json
|-- getinstances
|   |-- __init__.py
|   `-- getinstances.py
`-- template.yaml
```

If it looks slightly different, that's ok. As long as you have, at a bare minimum,
a `template.yaml` and a `.travis-ci.yml` file, as well as your function, you should be good to go.

At this point, if you commit and push your code to GitHub, it should trigger a job in Travis-CI. If
you navigate to the Travis-CI site, the UI should show your repository and job status. Pay attention
to the "Job Log", as that will show any errors or relevant output from the job.

If everything went well: Congratulations! You just did a CI deployment of a serverless function!

If you get any errors, check the output of the log for clues as to the root cause.
Travis-CI provides some documentation on [common failures as well](https://docs.travis-ci.com/user/common-build-problems/).

The last step we'll do is verify our Lambda function deployed correctly, via the AWS console.

## Verify It Works
Now it's time to make sure everything worked as it should have. Log in to your AWS account console,
and navigate to the "Lambda" service under "Compute". Make sure you're in the correct region(top
right). You should see your function. If the name has additional alphanumeric characters appended to
it, that's perfectly normal. The sam tool appends a unique ID to every function/stack it deploys.

Click on your function. At the top of the interface, you'll see a "Test" button next to a drop-down
menu that says *Select a test event..*

Test events provide simulated JSON payloads from various events in AWS that are used to trigger
Lambda functions. Go ahead and choose "Scheduled Event" from the "Event Template" drop down. Name
your event something meaningful like "TestServerlessEvent".

Once you've saved the event, click "Test". Depending on your function, you'll see the output
generated in the logs, or sent somewhere. In the case of the example provided in the tutorial, it
should show a JSON block listing active EC2 instances.

## Wrap Up
I'm hopeful this article series has provided at least a foundation for everyone to start thinking
about ways to streamline serverless development and deployment.

Some potential ideas to build on this project:

* Use the built-in Travis-CI Lambda provider.
* Add an API gateway to the project.
* Create a more complex commit/merge workflow for builds.
* Add unit-testing and code-coverage to builds.
* Add integration and functional testing to verify deployments.

Comments? Questions? Issues? Please post in the comments.

Until next time!
