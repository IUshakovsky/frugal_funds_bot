from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr
    mongo_uri: str
    bot_username: str
    db: str
    allowed_users: list

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()