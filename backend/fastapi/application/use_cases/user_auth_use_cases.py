from datetime import timedelta
from typing import List, Optional

from fastapi import HTTPException, status

from domain.entities import (
    AdministradorCreate,
    DocenteCreate,
    EstudianteCreate,
    RefreshTokenRequest,
    Token,
    TokenResponse,
    User,
    UserCreate,
    UserLogin,
)
from infrastructure.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, AuthService
from infrastructure.repositories.administrador_repository import SQLAdministradorRepository
from infrastructure.repositories.docente_repository import DocenteRepository
from infrastructure.repositories.estudiante_repository import SQLEstudianteRepository
from infrastructure.repositories.user_repository import SQLUserRepository


class UserAuthUseCase:
    def __init__(
        self,
        user_repository: SQLUserRepository,
        docente_repository: Optional[DocenteRepository] = None,
        estudiante_repository: Optional[SQLEstudianteRepository] = None,
        administrador_repository: Optional[SQLAdministradorRepository] = None,
    ):
        self.user_repository = user_repository
        self.docente_repository = docente_repository
        self.estudiante_repository = estudiante_repository
        self.administrador_repository = administrador_repository

    def register_user(self, user_data: UserCreate) -> User:
        """
        Registrar un nuevo usuario y crear automáticamente su perfil según el rol.

        Esta función garantiza que:
        1. Se crea el usuario en la tabla users
        2. Se crea automáticamente el perfil correspondiente según el rol:
           - Docente → tabla docentes
           - Estudiante → tabla estudiantes
           - Administrador → tabla administradores
        """
        # Verificar si el email ya existe
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado"
            )

        # Crear el usuario
        new_user = self.user_repository.create(user_data)

        # Crear perfil específico según el rol de forma atómica
        try:
            if new_user.rol == "docente":
                if not self.docente_repository:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Repositorio de docentes no configurado",
                    )
                # El departamento ahora es OBLIGATORIO y viene validado del schema
                docente_data = DocenteCreate(
                    user_id=new_user.id,
                    departamento=user_data.departamento,  # Ya validado como obligatorio
                )
                self.docente_repository.create(docente_data)

            elif new_user.rol == "estudiante":
                if not self.estudiante_repository:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Repositorio de estudiantes no configurado",
                    )
                # Generar matrícula automáticamente basada en el año actual y user_id
                from datetime import datetime
                current_year = datetime.now().year
                matricula = f"{current_year}{new_user.id:06d}"  # Ej: 2025000002
                
                estudiante_data = EstudianteCreate(
                    user_id=new_user.id,
                    matricula=matricula
                )
                self.estudiante_repository.create(estudiante_data)

            elif new_user.rol == "administrador":
                if not self.administrador_repository:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Repositorio de administradores no configurado",
                    )
                # Permisos por defecto si no se especifican
                permisos = user_data.permisos if hasattr(user_data, "permisos") and user_data.permisos else "ALL"
                administrador_data = AdministradorCreate(
                    user_id=new_user.id,
                    permisos=permisos
                )
                self.administrador_repository.create(administrador_data)

        except HTTPException:
            # Si falla la creación del perfil, eliminar el usuario creado
            # para mantener consistencia
            self.user_repository.delete(new_user.id)
            raise
        except Exception as e:
            # Si falla la creación del perfil por cualquier otra razón
            self.user_repository.delete(new_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear el perfil de {new_user.rol}: {str(e)}",
            )

        return new_user

    def login_user(self, login_data: UserLogin) -> Token:
        """Autenticar usuario y generar token"""
        # Autenticar usuario
        user = self.user_repository.authenticate(login_data.email, login_data.contrasena)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar si el usuario está activo
        if not self.user_repository.is_active(user):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")

        # Crear tokens de acceso y refresh
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Incluir información del usuario en el token
        token_data = {"sub": user.email, "user_id": user.id, "rol": user.rol}

        access_token = AuthService.create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        refresh_token = AuthService.create_refresh_token(
            data=token_data, expires_delta=refresh_token_expires
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # En segundos
            user=user,
            rol=user.rol,
        )

    def login_user_token_only(self, login_data: UserLogin) -> TokenResponse:
        """Autenticar usuario y generar token sin información del usuario"""
        # Autenticar usuario
        user = self.user_repository.authenticate(login_data.email, login_data.contrasena)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar si el usuario está activo
        if not self.user_repository.is_active(user):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")

        # Crear tokens de acceso y refresh
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Incluir información del usuario en el token
        token_data = {"sub": user.email, "user_id": user.id, "rol": user.rol}

        access_token = AuthService.create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        refresh_token = AuthService.create_refresh_token(
            data=token_data, expires_delta=refresh_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # En segundos
        )

    def get_current_user(self, token: str) -> User:
        """Obtener usuario actual desde token"""
        # Verificar token
        token_data = AuthService.verify_token(token)

        # Buscar usuario
        user = self.user_repository.get_by_email(token_data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron validar las credenciales",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    def get_current_active_user(self, token: str) -> User:
        """Obtener usuario actual activo"""
        current_user = self.get_current_user(token)
        if not self.user_repository.is_active(current_user):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
        return current_user

    def refresh_access_token(self, refresh_token_request: RefreshTokenRequest) -> Token:
        """Generar nuevo access token usando refresh token"""
        try:
            # Verificar refresh token
            token_data = AuthService.verify_refresh_token(refresh_token_request.refresh_token)

            # Buscar usuario
            user = self.user_repository.get_by_email(token_data.email)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verificar si el usuario está activo
            if not self.user_repository.is_active(user):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
                )

            # Crear nuevos tokens
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

            # Incluir información del usuario en los nuevos tokens
            token_data = {"sub": user.email, "user_id": user.id, "rol": user.rol}

            new_access_token = AuthService.create_access_token(
                data=token_data, expires_delta=access_token_expires
            )

            new_refresh_token = AuthService.create_refresh_token(
                data=token_data, expires_delta=refresh_token_expires
            )

            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user,
                rol=user.rol,
            )

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def refresh_access_token_only(
        self, refresh_token_request: RefreshTokenRequest
    ) -> TokenResponse:
        """Generar nuevo access token usando refresh token sin información del usuario"""
        try:
            # Verificar refresh token
            token_data = AuthService.verify_refresh_token(refresh_token_request.refresh_token)

            # Buscar usuario
            user = self.user_repository.get_by_email(token_data.email)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verificar si el usuario está activo
            if not self.user_repository.is_active(user):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
                )

            # Crear nuevos tokens
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

            # Incluir información del usuario en los nuevos tokens
            token_data = {"sub": user.email, "user_id": user.id, "rol": user.rol}

            new_access_token = AuthService.create_access_token(
                data=token_data, expires_delta=access_token_expires
            )

            new_refresh_token = AuthService.create_refresh_token(
                data=token_data, expires_delta=refresh_token_expires
            )

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def require_role(self, user: User, required_roles: List[str]) -> bool:
        """Verificar si el usuario tiene uno de los roles requeridos"""
        if user.rol not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(required_roles)}",
            )
        return True

    def require_admin(self, user: User) -> bool:
        """Verificar si el usuario es administrador"""
        return self.require_role(user, ["administrador"])

    def require_docente(self, user: User) -> bool:
        """Verificar si el usuario es docente"""
        return self.require_role(user, ["docente"])

    def require_estudiante(self, user: User) -> bool:
        """Verificar si el usuario es estudiante"""
        return self.require_role(user, ["estudiante"])

    def require_docente_or_admin(self, user: User) -> bool:
        """Verificar si el usuario es docente o administrador"""
        return self.require_role(user, ["docente", "administrador"])

    def get_user_specific_data(self, user: User) -> dict:
        """Obtener datos específicos del usuario según su rol"""
        result = {
            "user_id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "rol": user.rol,
            "activo": user.activo,
        }

        # Agregar datos específicos según el rol
        if user.rol == "docente" and user.docente:
            result["docente_info"] = {
                "id": user.docente.id,
                "departamento": user.docente.departamento,
            }
        elif user.rol == "estudiante" and user.estudiante:
            result["estudiante_info"] = {
                "id": user.estudiante.id,
                "matricula": user.estudiante.matricula,
            }
        elif user.rol == "administrador" and user.administrador:
            result["administrador_info"] = {
                "id": user.administrador.id,
                "permisos": user.administrador.permisos,
            }

        return result
