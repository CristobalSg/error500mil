import os
import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from domain.entities import TokenData

# Configuración de hashing de contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=13, bcrypt__ident="2b"
)


# Función auxiliar para obtener secretos de forma segura
def _get_secret_key(env_var: str, development_fallback: Optional[str] = None) -> str:
    """
    Obtener secret key de forma segura desde variables de entorno.

    En producción: requiere que la variable esté configurada.
    En desarrollo: permite fallback pero emite advertencia.

    Args:
        env_var: Nombre de la variable de entorno
        development_fallback: Valor por defecto solo para desarrollo

    Returns:
        El secret key configurado

    Raises:
        ValueError: Si la variable no está configurada en producción
    """
    env = os.getenv("NODE_ENV", "development")
    secret = os.getenv(env_var)

    if secret:
        return secret

    # En producción, forzar que esté configurado
    if env == "production":
        raise ValueError(
            f"CRITICAL: La variable {env_var} DEBE estar configurada en producción. "
            f"Genera un secret seguro usando: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    # En desarrollo, usar fallback pero advertir
    if development_fallback:
        warnings.warn(
            f"⚠️  Usando secret por defecto para {env_var} - SOLO PARA DESARROLLO",
            RuntimeWarning,
            stacklevel=2,
        )
        return development_fallback

    # Si no hay fallback, generar error
    raise ValueError(f"Variable de entorno {env_var} no configurada")


# Lista blanca de algoritmos permitidos (protección contra ataques de algoritmo None)
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512"]

# Configuración JWT desde variables de entorno
SECRET_KEY = _get_secret_key(
    "JWT_SECRET_KEY", development_fallback="dev_secret_not_for_production_use"
)

REFRESH_SECRET_KEY = _get_secret_key(
    "JWT_REFRESH_SECRET_KEY", development_fallback="dev_refresh_secret_not_for_production_use"
)

# Validar que el algoritmo esté en la lista blanca
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
if ALGORITHM not in ALLOWED_ALGORITHMS:
    raise ValueError(
        f"CRITICAL: Algoritmo JWT no permitido: {ALGORITHM}. "
        f"Usa uno de: {', '.join(ALLOWED_ALGORITHMS)}"
    )

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))

# Validación adicional: los secretos deben ser diferentes
if SECRET_KEY == REFRESH_SECRET_KEY:
    raise ValueError(
        "CRITICAL: JWT_SECRET_KEY y JWT_REFRESH_SECRET_KEY deben ser diferentes. "
        "Esto es un requisito de seguridad."
    )


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera el hash de la contraseña"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT de acceso"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT de refresh"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> TokenData:
        """
        Verifica y decodifica un token JWT con validación estricta

        Mejoras de seguridad:
        - Validación explícita de algoritmos permitidos
        - Verificación estricta de firma y expiración
        - Validación de todos los campos requeridos
        - Protección contra ataques de algoritmo None
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Opciones de validación estricta
            decode_options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,
                "require_exp": True,
            }

            if token_type == "access":
                # Decodificar con lista blanca de algoritmos
                payload = jwt.decode(
                    token, SECRET_KEY, algorithms=ALLOWED_ALGORITHMS, options=decode_options
                )
            elif token_type == "refresh":
                payload = jwt.decode(
                    token, REFRESH_SECRET_KEY, algorithms=ALLOWED_ALGORITHMS, options=decode_options
                )
            else:
                raise credentials_exception

            # Extraer y validar campos requeridos
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            rol: str = payload.get("rol")
            exp: int = payload.get("exp")
            token_type_payload: str = payload.get("type")

            # Verificar que TODOS los campos requeridos existan
            if not all([email, user_id, rol, exp, token_type_payload]):
                raise credentials_exception

            # Verificar que el tipo de token coincida
            if token_type_payload != token_type:
                raise credentials_exception

            token_data = TokenData(email=email, user_id=user_id, rol=rol, exp=exp)
            return token_data

        except JWTError:
            raise credentials_exception

    @staticmethod
    def verify_refresh_token(token: str) -> TokenData:
        """Verifica específicamente un refresh token"""
        return AuthService.verify_token(token, token_type="refresh")

    @staticmethod
    def create_tokens_for_user(user_data: dict) -> dict:
        """Crea tanto access token como refresh token para un usuario"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = AuthService.create_access_token(
            data=user_data, expires_delta=access_token_expires
        )

        refresh_token = AuthService.create_refresh_token(
            data=user_data, expires_delta=refresh_token_expires
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
