# third parties
from minio import Minio
from urllib3.exceptions import MaxRetryError
from w3k8s_adm.k8s_utils import get_secret, get_k8s_config, port_fwd_service

PORT_FWD_MINIO = 9143


async def start_minio_client(k8s_ctx: str):

    k8s_config = await get_k8s_config(k8s_ctx)
    print(f"✅ Successfully retrieved K8s configuration for context '{k8s_ctx}'")

    await port_fwd_service(
        k8s_config=k8s_config, namespace="infra", service="minio", port=PORT_FWD_MINIO
    )
    print(f"🔑 Use secret 'minio-admin-secret.admin-secret-key' for minio connection")
    secret: dict[str, str] = await get_secret(
        k8s_config=k8s_config, namespace_name="infra", secret_name="minio-admin-secret"
    )

    minio = Minio(
        endpoint=f"localhost:{PORT_FWD_MINIO}",
        access_key="admin",
        secret_key=secret["admin-secret-key"],
        secure=False,
    )
    try:
        # Try listing buckets
        buckets = minio.list_buckets()

        print(
            "🟢 Connected to minio, available buckets:",
            [bucket.name for bucket in buckets],
        )
    except MaxRetryError as e:
        print("🚫 Connection to minio failed:", str(e))
        exit(1)

    return minio
