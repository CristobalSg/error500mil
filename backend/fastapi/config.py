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
    
    # Agent API URL (para generación de horarios)
    agent_api_url: str = os.getenv("AGENT_API_URL", "http://agent:8200")
    
    # Service-to-Service Authentication
    # Token compartido entre backend y agent para comunicación interna
    # DEBE estar definido en variables de entorno por seguridad
    service_auth_token: str = os.getenv("SERVICE_AUTH_TOKEN")

    # CORS
    @property
    def cors_origins(self) -> List[str]:
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            return [origin.strip() for origin in cors_env.split(",")]

        raise ValueError(
            "CORS_ORIGINS no está definido correctamente en las variables de entorno."
        )

    # Usuario administrador inicial
    initial_admin_name: str = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    initial_admin_email: str = os.getenv("INITIAL_ADMIN_EMAIL", "admin@example.com")
    initial_admin_password: str = os.getenv("INITIAL_ADMIN_PASSWORD")

    # Usuarios de desarrollo 
    dev_docente_name: str = os.getenv("DEV_DOCENTE_NAME")
    dev_docente_email: str = os.getenv("DEV_DOCENTE_EMAIL")
    dev_docente_password: str = os.getenv("DEV_DOCENTE_PASSWORD")
    dev_docente_departamento: str = os.getenv("DEV_DOCENTE_DEPARTAMENTO", "INFORMATICA")
    
    dev_estudiante_name: str = os.getenv("DEV_ESTUDIANTE_NAME")
    dev_estudiante_email: str = os.getenv("DEV_ESTUDIANTE_EMAIL")
    dev_estudiante_password: str = os.getenv("DEV_ESTUDIANTE_PASSWORD")
    dev_estudiante_matricula: str = os.getenv("DEV_ESTUDIANTE_MATRICULA", "2024001")

    def __init__(self):
        # Validar configuraciones críticas
        if not all([self.database_url, self.postgres_db, self.postgres_user, self.postgres_password]):
            raise ValueError(
                "Configuraciones de BD faltantes. Verifica tus variables de entorno."
            )

# Instancia global
settings = Settings()
