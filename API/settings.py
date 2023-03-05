from pydantic import BaseSettings


class EnvVar(BaseSettings):
    HOSTNAME: str

    # Postgres db
    DB_HOSTNAME: str
    DB_PORT: str
    DB_NAME: str
    DB_USERNAME: str
    DB_USER_PASSWORD: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
    REDIS_DB: int
    REDIS_TIMEOUT: int

    class Config:
        env_file = ".env"


env = EnvVar()
