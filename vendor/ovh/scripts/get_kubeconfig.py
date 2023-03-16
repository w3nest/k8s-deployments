import os

import ovh
from dotenv import load_dotenv

load_dotenv()

client = ovh.Client(
    endpoint='ovh-eu',
    application_key=os.getenv("APPLICATION_KEY"),
    application_secret=os.getenv("APPLICATION_SECRET"),
    consumer_key=os.getenv("CONSUMER_KEY"),
)

result = client.post(f"/cloud/project/{os.getenv('SERVICE_NAME')}/kube/{os.getenv('KUBE_ID')}/kubeconfig")

print(result["content"])
