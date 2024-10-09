---
title: "DevSecOps: Add Docker Image Scanning To Your CI/CD Pipeline"
author: Mike Vanbuskirk
date: 2022-01-10
slug: "devsecops-add-docker-image-scanning-to-your-cicd-pipeline"
tags: 
  - devsecops
  - ci/cd
  - docker
  - github
categories: 
  - How-To
thumbnail: "docker_whale.jpg"
---

It's been over a year since I've last posted anything to the blog that wasn't commissioned writing. Maintaining consistency in writing definitely falls under a "hard" thing for me.

I think to get 2022 started right, I'll start with a short technical how-to. I've found others to be immensely helpful, so I enjoy any opportunity to contribute back to the same ecosystem.

This post will cover using [trivy](https://github.com/aquasecurity/trivy) and [GithHub Actions](https://github.com/features/actions) to add security scanning to Docker-based development workflows.


## Prerequisites 

- A GitHub account
- Comfortable with Git and Docker workflows.
- Familiarity with GitHub Actions and basic CI/CD concepts
- Basic knowledge of Flask/Python(feel free to substitute a different stack)
- An application that runs inside a Docker container(I'll be using a basic Flask app as an example)


## The "Why": DevSecOps 

Anyone that's lived through it will tell you that it's not fun to find a security vulnerability in a live production SLA environment. Customer data is potentially at risk, and the future of the company may be in doubt.

DevSecOps is a growing culture within DevOps that aims to shift more of the responsibility and implementation duty of security "left" in the software development lifecycle(SDLC). Imagine the life of an application, starting with design and the first lines of code written on the left of the timeline, and the final, live application on the right. The further left that security issues can be detected and remediated means fixes are easier to implement and less costly.

Developers working with Docker-based applications will often grab base images from public repositories without much thought as to the source. Unfortunately there have been multiple examples of [public images being compromised by malicious actors](https://www.trendmicro.com/vinfo/us/security/news/virtualization-and-cloud/malicious-docker-hub-container-images-cryptocurrency-mining). The good news is that DevOps teams can implement tools to detect and prevent compromise without having expend much effort on implementation. [Trivy](https://www.aquasec.com/products/trivy/), from Aquasec security, provides an open source tool that already has a [GitHub Action integration available](https://github.com/aquasecurity/trivy-action).


## Getting Started: The App 

For simplicity's sake, I'll use the basic "Hello World" Flask app from the [Flask quickstart](https://flask.palletsprojects.com/en/2.0.x/quickstart/).

My basic Dockerfile is as follows:

```dockerfile
FROM python:3.9

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app.py app.py

ENV FLASK_APP="hello"

CMD ["python", "app.py"]
```


## GitHub Actions Setup 

With GitHub Actions, we have access to a fully-featured CI/CD toolchain without needing to setup, deploy, and administer our own CI/CD infrastructure. I highly recommend [checking out their docs](https://docs.github.com/en/actions/learn-github-actions) if you're not familiar.

Similar to other solutions, GitHub Actions uses YAML files to configure CI/CD pipelines. For this example, we'll use `.github/workflows/main.yml`.

Start by creating a basic definition file that will allow the Docker container to be built in the pipeline:

```yaml
name: build
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Build the image
        run: docker build -t codevbus/flask-app -f Dockerfile .
```

Once this file is pushed to the repository, any subsequent push or pull request to the `main` branch will trigger this workflow, which will build the Docker container based on the Dockerfile in the base directory.


## Adding image scanning with Trivy 

The simple syntax of GitHub Actions configuration makes it easy to add additional steps to our workflow file. In this case, we'll be adding the Trivy vulnerability scanner:

```yaml
name: build
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Build the image
        run: docker build -t codevbus/flask-app -f Dockerfile .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: codevbus/flask-app
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH'
```

Once this change is pushed to the repo, the next run of GitHub Actions will use the Trivy action to perform a vulnerability scan of your Docker image and application dependencies.

Since I'm using a fairly up-to-date Python version and Docker container, and a very simple app, Trivy shows a clean bill of health:

```shell
codevbus/flask-app (debian 11.2)
================================
Total: 0 (HIGH: 0, CRITICAL: 0)


Python (python-pkg)
===================
Total: 0 (HIGH: 0, CRITICAL: 0)
```

You can view this output by going to "Actions", clicking through the most recent workflow run, and expanding the log output for the "Run Trivy vulnerability scanner" step(as we defined in the `main.yml` file)

If Trivy detected a vulnerability or issue of some kind, this line in the config:

```yaml
exit-code: '1'
```

ensures that a non-zero exit code is thrown and the action/workflow run will not succeed, throwing an obvious warning for further investigation.


## Wrap-up 

All done! You should now have a working CI/CD Docker-based development workflow with vulnerability scanning. The example I've provided is overly simple, but additional features could be added, such as commenting scan results to pull requests, or adding static code scanning.

All example code and config is provided here: <https://github.com/codevbus/flask-app>

Hopefully this has been helpful, happy hacking!
