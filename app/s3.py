import asyncio
import json
import os
from functools import partial

import boto3
from botocore.exceptions import ClientError

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "products")
MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")

_client = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)

_PUBLIC_POLICY = json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{MINIO_BUCKET}/*",
        }
    ],
})


def _ensure_bucket_sync() -> None:
    try:
        _client.head_bucket(Bucket=MINIO_BUCKET)
    except ClientError:
        _client.create_bucket(Bucket=MINIO_BUCKET)

    try:
        _client.put_bucket_policy(Bucket=MINIO_BUCKET, Policy=_PUBLIC_POLICY)
    except ClientError:
        pass


def _upload_file_sync(object_key: str, data: bytes, content_type: str) -> None:
    _client.put_object(
        Bucket=MINIO_BUCKET,
        Key=object_key,
        Body=data,
        ContentType=content_type,
    )


async def ensure_bucket_exists() -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _ensure_bucket_sync)


async def upload_file(object_key: str, data: bytes, content_type: str) -> str:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_upload_file_sync, object_key, data, content_type))
    return get_public_url(object_key)


def get_public_url(object_key: str) -> str:
    return f"{MINIO_PUBLIC_URL}/{MINIO_BUCKET}/{object_key}"
