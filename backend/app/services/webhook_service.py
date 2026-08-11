import json
import urllib.request
import urllib.error
from app.core.config import settings


def get_discord_webhook_for_campaign_type(campaign_type: str):
    campaign_type = (campaign_type or "").lower()

    general_webhook = getattr(settings, "DISCORD_GENERAL_WEBHOOK_URL", "")

    if "birthday" in campaign_type:
        return settings.DISCORD_BIRTHDAY_WEBHOOK_URL or general_webhook

    if "membership" in campaign_type or "member" in campaign_type:
        return settings.DISCORD_MEMBERSHIP_WEBHOOK_URL or general_webhook

    if "upgrade" in campaign_type:
        return settings.DISCORD_UPGRADE_WEBHOOK_URL or general_webhook

    if "winback" in campaign_type or "inactive" in campaign_type:
        return settings.DISCORD_WINBACK_WEBHOOK_URL or general_webhook

    return settings.DISCORD_LOG_WEBHOOK_URL or general_webhook

def send_discord_message(webhook_url: str, title: str, body: str, footer: str = "OmniLink CRM Demo"):
    print("Discord webhook URL loaded:", webhook_url[:60] if webhook_url else "EMPTY")

    if not webhook_url or webhook_url.startswith("PASTE_"):
        return {
            "success": True,
            "status": "simulated",
            "message": "No Discord webhook configured. Message simulated locally."
        }

    payload = {
        "username": "OmniLink CRM Campaign Bot",
        "content": f"**{title}**\n{body}\n\n_{footer}_"
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

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status_code = response.getcode()

            if 200 <= status_code < 300:
                return {
                    "success": True,
                    "status": "sent",
                    "status_code": status_code
                }

            return {
                "success": False,
                "status": "failed",
                "status_code": status_code,
                "message": "Discord returned non-success status"
            }

    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "status": "failed",
            "status_code": e.code,
            "message": str(e)
        }

    except Exception as e:
        return {
            "success": False,
            "status": "failed",
            "message": str(e)
        }