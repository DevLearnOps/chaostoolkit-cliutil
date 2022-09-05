import os
import re
import typing

import boto3
import botocore
from logzero import logger

_s3 = boto3.resource("s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL"))


def get_bucket_name_and_key_from_path(path: str) -> (str, str):
    if not (path and path.startswith("s3://")):
        raise ValueError(f"Path {path} is not a valid s3 location.")

    bucket, key = path.replace("s3://", "").split("/", 1)
    return (bucket, key)


def upload_file(source: str, path: typing.Optional[str] = None, **kwargs):
    if not source:
        raise ValueError(
            "Could not upload file to S3. Source file cannot be null"
        )
    if not os.path.exists(source):
        raise ValueError(
            "Could not upload file to S3. Source file does not exists"
        )

    if path:
        bucket_name, key = get_bucket_name_and_key_from_path(path)
        kwargs["Bucket"] = bucket_name
        kwargs["Key"] = key

    try:
        bucket = _s3.Bucket(kwargs.pop("Bucket"))
        bucket.upload_file(source, kwargs.pop("Key"), **kwargs)
    except botocore.exceptions.ClientError as error:
        logger.error("Could not upload file to S3. Client error.")
        raise error


def download_objects(path: str, outdir: str):
    bucket_name, prefix = get_bucket_name_and_key_from_path(path)
    if not prefix.endswith("/"):
        prefix += "/"

    bucket = _s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=prefix):
        destfile = os.path.join(
            outdir, re.sub(f"^{re.escape(prefix)}", "", obj.key)
        )
        destpath = os.path.dirname(destfile)
        print(outdir, prefix, destfile, destpath)

        if not os.path.exists(destpath):
            os.makedirs(destpath)

        bucket.download_file(Key=obj.key, Filename=destfile)
