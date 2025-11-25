from fastapi import APIRouter, Depends, HTTPException, status

from application.use_cases.user_auth_use_cases import UserAuthUseCase
from domain.authorization import Permission  # ✅ MIGRADO
from domain.entities import (  # Response models
    RefreshTokenRequest,
    Token,
    TokenResponse,
    User,
    UserLogin,
)
from domain.schemas import UserSecureCreate  # ✅ SCHEMAS SEGUROS
from infrastructure.dependencies import get_user_auth_use_case, require_permission  # ✅ MIGRADO

router = APIRouter()


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario (Solo Admin)",
    description="Crea un nuevo usuario en el sistema. **Requiere permisos de administrador (USER:CREATE)**",
)
async def register(
    user_data: UserSecureCreate,
    current_user: User = Depends(require_permission(Permission.USER_CREATE)),
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
):
    """Registrar un nuevo usuario (requiere permiso USER:CREATE - solo administradores)"""
    try:
        user = auth_use_case.register_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin, auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case)
):
    """Iniciar sesión y obtener token de acceso"""
    try:
        token = auth_use_case.login_user_token_only(login_data)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.post("/login-json", response_model=TokenResponse)
async def login_json(
    login_data: UserLogin, auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case)
):
    """Iniciar sesión con JSON y obtener token de acceso"""
    try:
        token = auth_use_case.login_user_token_only(login_data)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(require_permission(Permission.USER_READ)),  # ✅ MIGRADO
):
    """Obtener información del usuario actual (requiere permiso USER:READ)"""
    return current_user


@router.get("/me/detailed")
async def read_users_me_detailed(
    current_user: User = Depends(require_permission(Permission.USER_READ)),  # ✅ MIGRADO
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
):
    """Obtener información detallada del usuario actual incluyendo datos específicos del rol (requiere permiso USER:READ)"""
    return auth_use_case.get_user_specific_data(current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    auth_use_case: UserAuthUseCase = Depends(get_user_auth_use_case),
):
    """Refrescar access token usando refresh token"""
    try:
        new_token = auth_use_case.refresh_access_token_only(refresh_request)
        return new_token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor"
        )
