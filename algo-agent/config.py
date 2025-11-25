import os
from typing import List
from dotenv import load_dotenv
import pathlib


class Settings:
    # Base de datos
    database_url: str = os.getenv("DB_URL")
    postgres_db: str = os.getenv("POSTGRES_DB")
    postgres_user: str = os.getenv("POSTGRES_USER")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    # API Configuration
    environment: str = os.getenv("NODE_ENV", "development")
    debug: bool = environment == "development"
    
    # CORS
    @property
    def cors_origins(self) -> List[str]:
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            return [origin.strip() for origin in cors_env.split(",")]

        raise ValueError(
            "CORS_ORIGINS no está definido correctamente en las variables de entorno."
        )
        
    def __init__(self):
        # Validar configuraciones críticas
        if not all([self.database_url, self.postgres_db, self.postgres_user, self.postgres_password]):
            raise ValueError(
                "Configuraciones de BD faltantes. Verifica tus variables de entorno."
            )

# Instancia global
settings = Settings()