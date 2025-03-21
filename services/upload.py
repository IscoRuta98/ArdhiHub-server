import logging

import boto3
import boto3.resources
from botocore.exceptions import ClientError

from config.settings import settings

ACCESS_ID = settings.digital_ocean_access_key
SECRET_KEY = settings.digital_ocean_secret_key


s3_client = boto3.client('s3',
                  region_name='ams3',
                  endpoint_url='https://ams3.digitaloceanspaces.com', 
                  aws_access_key_id=ACCESS_ID, 
                  aws_secret_access_key=SECRET_KEY)



def upload_file_to_bucket(file_obj,
                          bucket_name: str = 'land-records',
                          s3_client = s3_client):
    """Upload a file to an S3 bucket

    :param file_obj: File to upload
    :param bucket: Bucket to upload to
    :param s3_client: S3 client
    :return: True if file was uploaded, else False
    """

    # Upload the file
    try:
        response = s3_client.upload_fileobj(file_obj.file, bucket_name, file_obj.filename)
        file_url = f"https://{bucket_name}.ams3.digitaloceanspaces.com/{file_obj.filename}"
        return file_url
    except ClientError as e:
        logging.error(e)
    
