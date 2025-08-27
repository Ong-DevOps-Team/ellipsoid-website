import os
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

# Determine environment and load appropriate .env file
app_env = os.getenv("APP_ENV", "development")

# Get the directory where this settings.py file is located
current_dir = Path(__file__).parent.parent

if app_env == "production":
    # For production, load environment_production.cfg
    env_file = current_dir / "environment_production.cfg"
    load_dotenv(env_file, override=True)
else:
    # For local development, load environment.cfg
    env_file = current_dir / "environment.cfg"
    load_dotenv(env_file, override=True)

class Settings:
    def __init__(self):
        # Database settings
        self.db_username: str = os.getenv("DB_USERNAME", "")
        self.db_password: str = os.getenv("DB_PASSWORD", "")
        self.fernet_key: str = os.getenv("FERNET_KEY", "")
        self.db_server: str = os.getenv("DB_HOST", "geog495db.database.windows.net")
        self.db_name: str = os.getenv("DB_NAME", "EllipsoidLabs")
        self.db_port: int = int(os.getenv("DB_PORT", "1433"))
        
        # API keys
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self.esri_api_key: str = os.getenv("ESRI_API_KEY", "")
        self.shipengine_api_key: str = os.getenv("SHIPENGINE_API_KEY", "")
        
        # Azure AI Language credentials
        self.azure_language_key: str = os.getenv("AZURE_LANGUAGE_KEY", "")
        self.azure_language_endpoint: str = os.getenv("AZURE_LANGUAGE_ENDPOINT", "")
        
        # MongoDB
        self.mongo_connection_string: str = os.getenv("MONGO_CONNECTION_STRING", "")
        
        # JWT settings
        self.jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        
        # Chat settings
        self.DEFAULT_SYSTEM_PROMPT: str = "You are a Geographic Information Systems (GIS) expert. Please help the user with their GIS questions and problems."
        
        # Application settings
        self.app_env: str = app_env
        self.log_level: str = os.getenv("LOG_LEVEL", "DEBUG")
        self.log_format: str = os.getenv("LOG_FORMAT", "human")

        # Logging settings (for backward compatibility)
        self.logging_priority_level: str = self.log_level

def get_settings() -> Settings:
    return Settings()
