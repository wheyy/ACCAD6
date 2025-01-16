# ACCAD6 Capstone Project

- Made by: Low King Whey(not the brand), Aaron Soh, Ang Ian, Tan Xeng Ian

## Core Services

- **Frontend**: Flask, hosted on AWS App Runner
- **Backend**: AWS Lambda, DynamoDB, S3
- **Deployment**: AWS App Runner, Docker on Amazon ECR with CodePipeline

We present **attendants**, an attendance taking app for students. This app aims to consolidate video upload and retrieval onto a single website.

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

```
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin <aws-link-here>
docker build -t <docker-image> .
docker tag <docker-image>:latest <aws-link-here>/<docker-image>:latest
docker push <aws-link-here>/<docker-image>:latest
```

Set up an Amazon CodeBuild project and set the primary source to your own GitHub repository. Enable privileged access under `Environment`, and set the buildspec file to the `buildspec.yml` file located in your repository. Set artifacts to none.

![image](https://github.com/user-attachments/assets/065dc762-8d36-4480-bd46-8afb9164c758)
<img src="https://github.com/user-attachments/assets/33c138ec-d713-44f6-91e7-6d4d8a6083ec" />

Run the CodeBuild project once, and an image should appear in your ECR repository.
![image](https://github.com/user-attachments/assets/539f00b6-232c-4005-9656-6d1216179ef0)

Create an AWS App Runner project and point it to your ECR repository. Set the deployment trigger to be automatic.
![image](https://github.com/user-attachments/assets/c07e673b-0ec2-41dc-a414-711cc57dd7d6)

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

## Usage

Each request is passed onto our AWS Lambda via a HTTP POST request. In each request, a `payload` must be specified:
```
{
    'action': 'upload',
    'params': {'object_name': filename}
}
```
The payload specifies a target `action`, which is one of the 4 CRUD operations supported. `params` are data to be passed into our function.

We can send our payload to our target endpoint (AWS Lambda function URL) via a POST request using the `requests` library. The response is a JSON object, with a response code in the form:
```
{
    'statusCode': 200,
    'body': json.dumps(response)
}
```
The value in the `body` can be accessed by parsing the response from the POST request with `.json()` so that Python can access it.

1. Pulling from database

In our application, we load entries in our database corresponding to the selected date on our frontend. When the `/view/{date}` page is loaded, the `date` value is sent as a parameter in our payload to perform a database query:
```
{
    'action': 'get_calendar',
    'params': {'date': date}
}
```
In our DynamoDB creation, we specified `timestamp` as a sort key for query purposes. AWS Lambda runs a database query to find entries with a matching date:
```
response = table.scan(
            FilterExpression='begins_with(#ts, :date)',
            ExpressionAttributeNames={
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues={
                ':date': date
            }
        )
```
and returns a list containing a `record` of the metadata associated with the entry, including a S3 url (read-only) to preview the file, which is then displayed on our frontend:
```
record = {
            'title': item.get('title'),
            'description': item.get('description'),
            'video_link': s3_url,
            'timestamp': item.get('timestamp'),
            'submission_id': int(item.get('submission_id'))
        }
```

2. Creating an upload

When the upload button is pressed, a payload containing the file name is sent via POST. To generate unique file names, the current server `datetime` is concatenated to the end of the file name.

In our AWS Lambda backend, a pre-signed S3 URL is generated with a short expiry time to upload the video. The `object_name` specifier is cross-checked against the POST request later on to ensure that only the correct file is being uploaded.

```
url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
                'ContentType': 'video/mp4'
            },
            ExpiresIn=expiration
        )
```

**Why pre-signed URLs?**

- Allows public uploads to our S3 bucket without exposing bucket endpoint
- No need for AWS credentials, no need for any secrets manager, etc
- Additional parameters can be specified to prevent abuse
- Grants temporary access only
  
The generated URL is then returned, which is then used to send our video data via a POST request:
```
requests.put(url,data=video.read(), headers={'Content-Type': 'video/mp4'})
```
Note that the video data being sent must be passed as raw binary data, or else the upload will fail.

If the video upload succeeds, a `200 OK` response is returned. We can then continue to write the metadata associated with the video into our database:
```
submission_id = uuid.uuid4().int & (1<<32)-1
timestamp = datetime.now().replace(microsecond=0).isoformat()
            
payload = {'action': 'write_to_db',
    'params': {
        'user_id':1,
        'submission_id': submission_id,
        'object_name':filename,
        'timestamp': timestamp,
        'title':title,
        'description': description
        }
    }
```
```
requests.post(LAMBDA_FUNCTION_URL, json=payload, headers={'Content-Type': 'application/json'})
```
A unique UUID is generated (and shortened to 32 bits), along with the current server datetime, and is packaged into a payload.
