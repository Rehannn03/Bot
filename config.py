from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    api_secret: str
    testnet: bool = True


    class Config:
        env_file = ".env"