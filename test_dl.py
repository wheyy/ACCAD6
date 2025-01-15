import boto3
from botocore.exceptions import ClientError

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
                'Key': object_name,
                'ResponseContentType': 'video/mp4'
            },
            ExpiresIn=expiration
        )
        return {'body': url, 'statusCode': 200}
    except ClientError as e:
        print(f"Error: {e}")
        return {'body': None, 'statusCode': 500}

if __name__ == '__main__':
    bucket_name = "accad-6-attendance-app-bucket"
    video_name = "test_video.mp4"
    
    response = generate_view_url(bucket_name, video_name)
    print(response)
