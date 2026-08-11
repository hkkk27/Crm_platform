# from pydantic import BaseModel
# from typing import Optional


# class LoginRequest(BaseModel):
#     email: str
#     role: str


# class CampaignCreateRequest(BaseModel):
#     campaign_name: str
#     campaign_type: str
#     channel: str
#     target_segment: str
#     created_by: Optional[str] = "CRM User"


# class ConsentUpdateRequest(BaseModel):
#     customer_id: str
#     whatsapp_consent: Optional[bool] = None
#     sms_consent: Optional[bool] = None
#     email_consent: Optional[bool] = None
#     app_notification_consent: Optional[bool] = None
#     personalization_consent: Optional[bool] = None
#     do_not_contact: Optional[bool] = None

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class ConsentUpdateRequest(BaseModel):
    customer_id: str
    whatsapp_consent: Optional[bool] = None
    sms_consent: Optional[bool] = None
    email_consent: Optional[bool] = None
    app_notification_consent: Optional[bool] = None
    personalization_consent: Optional[bool] = None
    do_not_contact: Optional[bool] = None


class CampaignCreateRequest(BaseModel):
    campaign_name: str
    campaign_type: str
    channel: str
    target_segment: str
class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str
