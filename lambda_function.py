import boto3
from botocore.exceptions import ClientError
import json

def lambda_handler(event, context):
    '''
    This function handles incoming HTTP requests.

    Parameters:
    event - A dictionary containing the action type and params
        eg. {
                "action": "generate_view_url",
                "params": {"object_name": "test_video.mp4"}
            }
    context - not used
    '''

    body = json.loads(event['body'])
    action = body['action']
    params = body['params']

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

    elif action == 'generate_view_url':
        object_name = params.get('object_name')
        return generate_view_url('accad-6-attendance-app-bucket', object_name)
    
    return {
        'statusCode': 400,
        'body': json.dumps(f'Invalid action {action}')
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
                'Key': object_name
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

def generate_view_url(bucket_name: str, object_name: str, expiration=30):
    '''
    This function generates a url to view the uploaded object.

    Parameters:
    bucket_name - default, accad-6-attendance-app-bucket
    object_name - video file name. eg: test_video.mp4
    expiration - default: 30. time in seconds before link expires
    '''
    s3_client = boto3.client('s3')
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
        return {'body': url, 'statusCode': 200}
    except ClientError as e:
        print(f"Error: {e}")
        return {'body': None, 'statusCode': 500}