"""Boto3 S3 Helper"""

import boto3
from botocore.config import Config


class S3Helper:
    """S3 Helper"""

    def __init__(self):
        """Initialize the S3 Helper."""
        s3 = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="rustfsadmin",
            aws_secret_access_key="rustfsadmin",
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

        bucket_name = "my-bucket"

        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket {bucket_name} created.")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"Bucket {bucket_name} already exists.")


if __name__ == "__main__":
    S3Helper()
