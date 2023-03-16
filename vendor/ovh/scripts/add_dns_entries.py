import json
import os
import sys

import ovh
from dotenv import load_dotenv

load_dotenv()

zone_name = os.getenv('ZONE_NAME')
name = sys.argv[1]
ip = sys.argv[2]
env = f".{sys.argv[3]}" if len(sys.argv) > 3 else ""

client = ovh.Client(
    endpoint='ovh-eu',
    application_key=os.getenv("APPLICATION_KEY"),
    application_secret=os.getenv("APPLICATION_SECRET"),
    consumer_key=os.getenv("CONSUMER_KEY"),
)

result_a = client.post(
    f"/domain/zone/{zone_name}/record",
    fieldType="A",
    subDomain=f"{name}",
    target=ip,
)
print(f"Response for {name}.{zone_name}. A {ip}")
print(json.dumps(result_a, indent=4))

result_l = client.post(
    f"/domain/zone/{zone_name}/record",
    fieldType="CNAME",
    subDomain=f"l{env}",
    target=f"{name}.{zone_name}.",
)

print(f"Response for l{env}.{zone_name}. CNAME {name}.{zone_name}.")
print(json.dumps(result_l, indent=4))

result_platform = client.post(
    f"/domain/zone/{zone_name}/record",
    fieldType="CNAME",
    subDomain=f"platform{env}",
    target=f"{name}.{zone_name}.",
)

print(f"Response for platform{env}.{zone_name}. CNAME {name}.{zone_name}.")
print(json.dumps(result_platform, indent=4))

result_tooling = client.post(
    f"/domain/zone/{zone_name}/record",
    fieldType="CNAME",
    subDomain=f"tooling{env}",
    target=f"{name}.{zone_name}.",
)

print(f"Response for tooling{env}.{zone_name}. CNAME {name}.{zone_name}")
print(json.dumps(result_tooling, indent=4))
