import boto3
from botocore.exceptions import ClientError

def insert_to_db(submission_id, timestamp, user_id, s3_reference, description):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accad-6-attendance-app-dynamodb')

    try:
        response = table.put_item(
            Item={
                'submission_id': submission_id,
                'timestamp': timestamp,
                'user_id': user_id,
                's3_reference': s3_reference,
                'description': description
            }
        )
        return {
            'statusCode': 200,
            'body': 'Table insert success'
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
    
if __name__ == '__main__':
    metadata = {
    'submission_id': 12345,
    'timestamp': '2025-01-15T10:00:00Z',
    'user_id': 'user_001',
    's3_reference': 's3://accad-6-attendance-app-bucket/test_video.mp4',
    'description': 'Attendance video for January 15, 2025'
    }

    result = insert_to_db(**metadata)
    print(result)