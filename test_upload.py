import boto3
import requests
from botocore.exceptions import ClientError

def url_gen(bucket_name: str, object_name: str, expiration=30):
    '''
    Generate a presigned URL to upload a file to S3.

    Parameters:
    bucket_name - default, accad-6-attendance-app-bucket
    object_name - video file name. eg: test_video.mp4
    expiration - default: 30. time in seconds before link expires
    '''
    s3_client = boto3.client('s3')

    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
        return {'body': url, 'statusCode': 200}
    
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return {'body': None, 'statusCode': 500}


if __name__ == '__main__':

    bucket_name = 'accad-6-attendance-app-bucket'
    video_name = 'test_video3.mp4'
    expiration = 20

    response = url_gen(bucket_name, video_name, expiration)
    print(f"Presigned URL response: {response}")

    if response['statusCode'] != 200:
        print("Failed to generate presigned URL")
        exit(1)

    url = response['body']  
    
    try:
        with open(video_name, 'rb') as f:
            files = f.read()
            response = requests.put(url, data=files)
            print(f'Status: {response.status_code}')

            if response.status_code != 200:
                print(f'Error: {response.text}')

    except FileNotFoundError:
        print(f"Error: Could not find file {video_name}")

    except Exception as e:
        print(f"Error during upload: {e}")