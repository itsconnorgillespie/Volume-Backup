import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from src.logger import get_logger
from src.settings import Settings

logger = get_logger()


def get_s3_client(settings: Settings) -> BaseClient:
    """ Creates a new S3 client instance. """
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def upload_s3_file(client: BaseClient, settings: Settings, path: str, key: str) -> bool:
    """ Upload the file at the given local path to S3. """
    try:
        client.upload_file(path, settings.S3_BUCKET, key)
        return True
    except (BotoCoreError, ClientError, S3UploadFailedError) as error:
        logger.error(f"Failed to upload the provided file to S3. | {error}")
        return False
