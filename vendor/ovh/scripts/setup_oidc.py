import json
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

result = client.post(
    f"/cloud/project/{os.getenv('SERVICE_NAME')}/kube/{os.getenv('KUBE_ID')}/openIdConnect",
    issuerUrl="https://platform.youwol.com/auth/realms/kubernetes",
    clientId="kubernetes-auth",
    usernameClaim="upn",
    usernamePrefix="sso:"
    groupsClaim=["groups"],
    groupsPrefix="sso:"
)

print(json.dumps(result, indent=4))
