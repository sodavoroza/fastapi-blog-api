import os
import boto3
from uuid import uuid4

def upload_image_to_s3(file_data: bytes, filename: str) -> str:
    s3_endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    s3_bucket = os.getenv("MINIO_BUCKET", "blog-uploads")
    s3_access_key = os.getenv("MINIO_ACCESS_KEY")
    s3_secret_key = os.getenv("MINIO_SECRET_KEY")

    s3 = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
    )

    unique_name = f"{uuid4()}_{filename}"
    s3.put_object(
        Bucket=s3_bucket,
        Key=unique_name,
        Body=file_data,
        ContentType="image/jpeg", 
    )
    image_url = f"{s3_endpoint}/{s3_bucket}/{unique_name}"
    return image_url
