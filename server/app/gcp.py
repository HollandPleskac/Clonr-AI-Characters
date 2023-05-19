import os

from google.cloud import storage

GCP_SA_PATH = os.environ.get("GCP_PATH")
client = storage.Client.from_service_account_json(GCP_SA_PATH)


def get_bucket(bucket_name):
    bucket = client.get_bucket(bucket_name)
    if not bucket.exists():
        bucket = create_bucket(bucket_name)
    return bucket


def create_bucket(bucket_name, storage_class="STANDARD", location="us-central1"):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = storage_class
    bucket = storage_client.create_bucket(bucket, location=location)
    return f"Bucket {bucket.name} successfully created."


def get_blob(bucket_name, blob_name):
    bucket = get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    return blob


def list_blobs(bucket_name, prefix=None):
    bucket = get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return blobs


def upload_blob(bucket_name, blob_name, file_path):
    bucket = get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    return blob.public_url
