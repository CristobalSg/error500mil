"""
Configuración de logging para la aplicación.
"""

import logging
import sys
from pathlib import Path

# Crear directorio de logs si no existe
log_dir = Path("/app/logs")
log_dir.mkdir(exist_ok=True)

# Formato de logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str = "INFO"):
    """
    Configura el sistema de logging de la aplicación.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convertir string a nivel de logging
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Crear handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    error_handler = logging.FileHandler(log_dir / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    security_file_handler = logging.FileHandler(log_dir / "security.log", encoding="utf-8")
    security_file_handler.setLevel(logging.INFO)
    security_file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Configuración del root logger
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            console_handler,
            file_handler,
            error_handler,
            security_file_handler,
        ],
    )

    # Configurar loggers específicos

    # Logger de seguridad
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_handler = logging.FileHandler(log_dir / "security.log", encoding="utf-8")
    security_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    security_logger.addHandler(security_handler)

    # Logger de rate limiting
    rate_limit_logger = logging.getLogger("rate_limit")
    rate_limit_logger.setLevel(logging.WARNING)

    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    logging.info("Sistema de logging configurado correctamente")


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.

    Args:
        name: Nombre del logger (generalmente __name__ del módulo)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
