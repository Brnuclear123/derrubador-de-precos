from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    ENV: str = Field(default="dev")
    TZ: str = Field(default="America/Sao_Paulo")

    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)

    DATABASE_URL: str = Field(default="sqlite:///./data.db")

    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIMS_SUB: str = "mailto:you@example.com"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "Derrubador <alerts@derruba.dev>"

    # Configurações de Proxy
    PROXY_ENABLED: bool = Field(default=False)
    PROXY_LIST: str = Field(default="")  # Lista de proxies separados por vírgula
    PROXY_USERNAME: str = Field(default="")
    PROXY_PASSWORD: str = Field(default="")
    PROXY_ROTATION_INTERVAL: int = Field(default=300)  # 5 minutos em segundos
    PROXY_MAX_RETRIES: int = Field(default=3)

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
