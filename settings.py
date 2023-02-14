from pydantic import BaseSettings


class EnvVar(BaseSettings):
    DB_HOSTNAME: str
    DB_PORT: str
    DB_NAME: str
    DB_USERNAME: str
    DB_USER_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str

    class Config:
        env_file = ".env"


env = EnvVar()
