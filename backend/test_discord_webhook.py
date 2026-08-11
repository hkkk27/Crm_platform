import json
import urllib.request
from app.core.config import settings

webhook_url = settings.DISCORD_GENERAL_WEBHOOK_URL

print("Webhook loaded:", webhook_url[:70] if webhook_url else "EMPTY")

payload = {
    "username": "OmniLink Test Bot",
    "content": "✅ Test message from OmniLink CRM backend."
}

data = json.dumps(payload).encode("utf-8")

request = urllib.request.Request(
    webhook_url,
    data=data,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "OmniLinkCRM/1.0"
    },
    method="POST"
)

with urllib.request.urlopen(request, timeout=10) as response:
    print("Discord status:", response.getcode())