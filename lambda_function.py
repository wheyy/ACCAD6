import boto3
from botocore.exceptions import ClientError
import json

def lambda_handler(event, context):
    '''
    This function handles incoming HTTP requests.

    Parameters:
    event - A dictionary containing the action type and params
        eg. {
                "action": "delete",
                "params": {"submission_id": 123, "timestamp": "2025-01-15T00:00:00}
            }
    context - not used
    '''

    body = json.loads(event['body'])
    # body = event
    action = body['action']
    params = body['params']

    if action == 'delete':
        submission_id = params.get('submission_id')
        timestamp = params.get('timestamp')
        return delete_entry(submission_id, timestamp)

    if action == 'get_calendar':
        date = params.get('date')
        return get_calendar_entries(date)
    
    if action == 'get_single_entry':
        submission_id = params.get('submission_id')
        timestamp = params.get('timestamp')
        return get_single_entry(submission_id, timestamp)
    
    if action == 'update_entry':
        submission_id = params.get('submission_id')
        timestamp = params.get('timestamp')
        title = params.get('title')
        description = params.get('description')
        return update_entry(submission_id, timestamp, title, description)

    if action == 'upload':
        object_name = params.get('object_name')
        expiration = int(params.get('expiration', 30))
        upload_response = upload('accad-6-attendance-app-bucket', object_name, expiration)
        return dict(upload_response)
    
    if action == 'write_to_db':
        submission_id = params.get('submission_id')
        timestamp = params.get('timestamp')
        user_id = params.get('user_id')
        object_name = params.get('object_name')
        title = params.get('title')
        description = params.get('description')
        return insert_to_db(submission_id, timestamp, user_id, object_name, title, description)
    
    return {
        'statusCode': 400,
        'body': json.dumps(f'Invalid action {action}')
    }

def get_single_entry(submission_id, timestamp):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accad-6-attendance-app-dynamodb')
    
    try:
        response = table.get_item(
            Key={
                'submission_id': submission_id,
                'timestamp': timestamp
            }
        )
        
        if 'Item' in response:
            item = response['Item']
            record = {
                'title': item.get('title'),
                'description': item.get('description'),
                'video_link': f"https://accad-6-attendance-app-bucket.s3.ap-southeast-1.amazonaws.com/{item.get('object_name')}",
                'timestamp': item.get('timestamp'),
                'submission_id': int(item.get('submission_id')),
                'object_name': item.get('object_name')
            }
            return {
                'statusCode': 200,
                'body': json.dumps(record)
            }
        return {
            'statusCode': 404,
            'body': json.dumps('Entry not found')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def update_entry(submission_id, timestamp, title, description):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accad-6-attendance-app-dynamodb')
    
    try:
        response = table.update_item(
            Key={
                'submission_id': submission_id,
                'timestamp': timestamp
            },
            UpdateExpression='SET title = :t, description = :d',
            ExpressionAttributeValues={
                ':t': title,
                ':d': description
            },
            ReturnValues='ALL_NEW'
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Entry updated successfully')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def delete_entry(submission_id, timestamp):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accad-6-attendance-app-dynamodb')
    
    try:
        response = table.delete_item(
            Key={
                'submission_id': submission_id,
                'timestamp': timestamp
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Entry deleted successfully')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_calendar_entries(date):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accad-6-attendance-app-dynamodb')
    
    try:
        response = table.scan(
            FilterExpression='begins_with(#ts, :date)',
            ExpressionAttributeNames={
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues={
                ':date': date
            }
        )
        print(f"DynamoDB response: {response}")
        items = response['Items']
        calendar_records = []
        
        for item in items:
            # get permanent s3 url
            s3_url = f"https://accad-6-attendance-app-bucket.s3.ap-southeast-1.amazonaws.com/{item.get('object_name')}"
            record = {
                'title': item.get('title'),
                'description': item.get('description'),
                'video_link': s3_url,
                'timestamp': item.get('timestamp'),
                'submission_id': int(item.get('submission_id'))
            }
            calendar_records.append(record)
            
        return {
            'statusCode': 200,
            'body': json.dumps(calendar_records)
        }
        
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def upload(bucket_name: str, object_name: str, expiration=30):
    '''
    Generate a presigned URL to upload a file to S3.

    Parameters:
    bucket_name - default, accad-6-attendance-app-bucket
    object_name - video file name. eg: test_video.mp4
    expiration - default: 30. time in seconds before link expires

    Returns:
    statusCode - HTTP response code
    body - Presigned S3 URL in json format
    '''
    if not object_name:
        return {
            'statusCode': 400,
            'body': json.dumps('object_name is required')
        }

    s3_client = boto3.client('s3', region_name='ap-southeast-1')

    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
                'ContentType': 'video/mp4'
            },
            ExpiresIn=expiration
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'url': url})
        }
    
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def insert_to_db(submission_id, timestamp, user_id, object_name, title, description):
    if not all([submission_id, timestamp, user_id, object_name]):
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required parameters')
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accad-6-attendance-app-dynamodb')

    try:
        response = table.put_item(
            Item={
                'submission_id': submission_id,
                'timestamp': timestamp,
                'user_id': user_id,
                'object_name': object_name,
                'title': title,
                'description': description
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('DDB table insert success')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }