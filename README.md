# ACCAD6 Capstone Project

- Made by: Low King Whey(not the brand), Aaron Soh, Ang Ian, Tan Xeng Ian

## Core Services

- **Frontend**: Flask, hosted on AWS App Runner
- **Backend**: AWS Lambda, DynamoDB, S3
- **Deployment**: AWS App Runner, Docker on Amazon ECR with CodePipeline

## Deliverables

- [x] **Set up frontend with Flask**
- [x] **Set up AWS Lambda, DynamoDB, and S3**
- [x] **Implement CRUD functions**
- [x] **Integrate frontend with AWS Lambda backend**
- [ ] **Perform unit tests**

## Setup

To run locally, clone this repo first:
```
git clone https://github.com/wheyy/ACCAD6
```

Set up a virtual environment with your favourite provider and install dependencies:
```
pip install -r requirements.txt
```

Create an S3 bucket and update the bucket policy to allow public read-only access:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadForGetBucketObjects",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<your-bucket-name>/*"
        }
    ]
}
```

Create a DynamoDB table with `submission_id:int` as partition key and `timestamp:str` as sort key.

Create a new Amazon ECR private repository, and take note of the push commands. Add them to a `buildspec.yml` file and put it in your folder's root directory.

Set up an Amazon CodeBuild project and set the primary source to your own GitHub repository. Enable privileged access under `Environment`, and set the buildspec file to the `buildspec.yml` file located in your repository.

Run the CodeBuild project once, and an image should appear in your ECR repository.

Create an AWS App Runner project and point it to your ECR repository. Set the deployment trigger to be automatic.

Create an AWS Lambda function with a Python runtime to use with `boto3`. Make sure to
- Allow CORS in AWS Lambda and set origin to App Runner URL
- Set AWS Lambda execution role to allow it to interact with S3 and DynamoDB:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObject",
                "s3:ListBucket",
                "dynamodb:GetItem",
                "dynamodb:GetRecords",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DeleteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": [
                "arn:aws:s3:::<your-bucket-name>/*",
                "arn:aws:dynamodb:*:*:table/<your-table-name>"
            ]
        }
    ]
}
```

Create another CodeBuild project for unit tests, use a different `testspec.yml` file instead.

Lastly, set up CodePipeline with CodeBuild to complete the CI/CD pipeline.
