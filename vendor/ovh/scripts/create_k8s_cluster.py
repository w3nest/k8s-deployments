import json
import os
import sys

import ovh
from dotenv import load_dotenv

load_dotenv()

name = sys.argv[1]

client = ovh.Client(
    endpoint='ovh-eu',
    application_key=os.getenv("APPLICATION_KEY"),
    application_secret=os.getenv("APPLICATION_SECRET"),
    consumer_key=os.getenv("CONSUMER_KEY"),
)

result = client.post(
    f"/cloud/project/{os.getenv('SERVICE_NAME')}/kube",
    region="GRA9",
    name=name,
    nodepool={
        "desiredNodes": 3,
        "minNodes": 0,
        "maxNodes": 5,
        "flavorName": "b2-15",
    },
    updatePolicy="ALWAYS_UPDATE",
    version="1.25"
)

print(json.dumps(result, indent=4))
