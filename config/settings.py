from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_db_uri: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    signing_algorithm: str
    signing_secret_key: str
    access_token_expire_minutes: int
    encryption_key: str
    digital_ocean_access_key: str
    digital_ocean_secret_key: str
    algod_address: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
