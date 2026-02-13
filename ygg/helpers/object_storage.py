"""Boto3 S3 Helper"""

import boto3
from botocore.config import Config

from ygg.config import YggS3Config, YggSetup
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="S3Connector")


class S3Connector:
    """S3 Connector"""

    def __init__(self, s3_client_config: YggS3Config):
        """Initialize the S3 Helper."""

        if not s3_client_config:
            logs.error("S3 Client Config cannot be empty.")
            raise ValueError("S3 Client Config cannot be empty.")

        self._s3 = boto3.client(
            "s3",
            endpoint_url=f"http://{s3_client_config.endpoint_url}",
            aws_access_key_id=s3_client_config.aws_access_key_id,
            aws_secret_access_key=s3_client_config.aws_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name=s3_client_config.region_name,
        )

    def create_bucket(self, bucket_name: str) -> None:
        """Create a bucket."""

        if not bucket_name:
            logs.error("Bucket name cannot be empty.")
            raise ValueError("Bucket name cannot be empty.")

        logs.debug("Trying to create a new bucket.", bucket_name=bucket_name)
        try:
            self._s3.create_bucket(Bucket=bucket_name)
            logs.info("Bucket created.", bucket_name=bucket_name)

        except self._s3.exceptions.BucketAlreadyOwnedByYou:
            logs.info("Bucket already exists.", bucket_name=bucket_name)


if __name__ == "__main__":
    ys = YggSetup().ygg_s3_config
    S3Connector(s3_client_config=ys).create_bucket("repository22")
