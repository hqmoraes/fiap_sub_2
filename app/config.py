from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "fiap-vehicles"
    app_env: str = "local"
    log_level: str = "INFO"
    api_port: int = 8000

    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "fiap_vehicles"
    db_user: str = "fiap"
    db_password: str = "fiap"

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False

settings = Settings()
