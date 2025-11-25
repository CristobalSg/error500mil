import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List


def _parse_cors(origins_raw: str | None) -> List[str]:
    if not origins_raw:
        return ["*"]
    return [origin.strip() for origin in origins_raw.split(",") if origin.strip()]


@dataclass
class AppSettings:
    """Application level settings without the overhead of a complex config layer."""

    title: str = "SGH - Sistema de Gestión de Horarios"
    version: str = "1.0.0"
    description: str = (
        "API que coordina la ejecución de FET: recolección de datos, "
        "generación del archivo de entrada y ejecución del algoritmo."
    )
    environment: str = field(default_factory=lambda: os.getenv("NODE_ENV", "development"))
    debug: bool = field(init=False)
    cors_origins: List[str] = field(default_factory=lambda: _parse_cors(os.getenv("CORS_ORIGINS")))
    fet_binary_path: Path = field(
        default_factory=lambda: Path(os.getenv("FET_BINARY_PATH", "/app/algorithm/fet-7.5.5/fet-cl"))
    )
    fet_workdir: Path = field(
        default_factory=lambda: Path(os.getenv("FET_WORKDIR", "/tmp/fet-jobs"))
    )
    fet_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("FET_TIMEOUT_SECONDS", "120"))
    )
    
    # Service-to-Service Authentication
    # Token compartido para validar peticiones del backend
    service_auth_token: str = field(
        default_factory=lambda: os.getenv("SERVICE_AUTH_TOKEN", "")
    )

    def __post_init__(self) -> None:
        self.debug = self.environment == "development"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


__all__ = ["AppSettings", "get_settings"]
