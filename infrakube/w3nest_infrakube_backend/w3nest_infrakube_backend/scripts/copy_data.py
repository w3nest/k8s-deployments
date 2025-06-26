import json
import os
from pathlib import Path

from minio import Minio
from tqdm import tqdm

from w3nest_infrakube_backend.routers.w3nest.router import minio_client

PORT_FWD_MINIO = 9143


def ensure_buckets(minio: Minio):
    buckets = ["webpm", "assets", "webpm-sessions-storage", "files", "docdb"]
    for bucket in buckets:
        if not minio.bucket_exists(bucket_name=bucket):
            minio.make_bucket(bucket_name=bucket)
            print(f"✅ bucket {bucket} created")


async def copy_db(db_path: Path, k8s_ctx: str):
    """
    Copy source data in minio's buckets, e.g.:
    ```python
    task = copy_db(
        db_path=Path.home() / 'Projects' / 'db-folder',
        k8s_ctx="minikube"
    )
    asyncio.run(task)
    ```
    Parameters:
        db_path: Path to the root folder of the database.
        k8s_ctx: Name of the K8s context.
    """

    minio = await minio_client(k8s_ctx=k8s_ctx)
    ensure_buckets(minio)

    storage_path = db_path / "storage"
    storage_files = [
        f
        for f in list(storage_path.rglob("*"))
        if f.is_file() and (f.parent / f"{f.name}.metadata.json").is_file()
    ]
    for file in tqdm(storage_files):
        relative_path = file.relative_to(storage_path)
        bucket_name = relative_path.parts[0]
        relative_path = file.relative_to(storage_path / bucket_name)
        file_data = open(file, "rb")
        metadata_bytes = open(f"{file}.metadata.json", "rb")
        metadata = json.load(metadata_bytes)
        minio.put_object(
            bucket_name=bucket_name,
            object_name=str(relative_path),
            data=file_data,
            length=os.stat(file).st_size,
            content_type=metadata["contentType"],
            metadata=metadata,
        )
    docdb_path = db_path / "docdb"
    docdb_files = [f for f in list(docdb_path.rglob("**/data.json")) if f.is_file()]

    for file in tqdm(docdb_files):
        bucket_name = "docdb"
        relative_path = file.relative_to(docdb_path)
        metadata = {"contentType": "application/json", "contentEncoding": "identity"}
        file_data = open(file, "rb")
        minio.put_object(
            bucket_name=bucket_name,
            object_name=str(relative_path),
            data=file_data,
            length=os.stat(file).st_size,
            content_type=metadata["contentType"],
            metadata=metadata,
        )
