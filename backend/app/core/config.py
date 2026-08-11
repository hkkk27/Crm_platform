from pydantic_settings import BaseSettings #rules md and check 
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "OmniLink CRM Backend"
    APP_ENV: str = "development"

    DB_PATH: str = "omnilink_crm.db"

    JWT_SECRET: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    DISCORD_BIRTHDAY_WEBHOOK_URL: str = ""
    DISCORD_MEMBERSHIP_WEBHOOK_URL: str = ""
    DISCORD_UPGRADE_WEBHOOK_URL: str = ""
    DISCORD_WINBACK_WEBHOOK_URL: str = ""
    DISCORD_LOG_WEBHOOK_URL: str = ""
    DISCORD_GENERAL_WEBHOOK_URL: str = ""

    FRONTEND_ORIGINS: str = "http://localhost:3002,http://127.0.0.1:3002"

    MAIL_HOST: str = "smtp-mail.outlook.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    PASSWORD_RESET_EXPIRE_MINUTES: int = 10

    @property #inumerator of 
    def allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",")]

    # @property
    # def allowed_origins(self) -> list[str]:
    # cleaned_origins = []
    
    # for origin in self.FRONTEND_ORIGINS.split(","):
    #     cleaned_origins.append(origin.strip())
        
    # return cleaned_origins


    class Config:
        env_file = ".env"


settings = Settings()

#pydandtic - md