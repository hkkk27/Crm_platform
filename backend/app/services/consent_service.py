def is_customer_eligible_for_channel(consent: dict, channel: str):
    if not consent:
        return False

    if consent.get("do_not_contact"):
        return False

    channel = channel.lower()

    if channel == "whatsapp":
        return consent.get("whatsapp_consent", False)

    if channel == "sms":
        return consent.get("sms_consent", False)

    if channel == "email":
        return consent.get("email_consent", False)

    if channel == "app":
        return consent.get("app_notification_consent", False)

    return False