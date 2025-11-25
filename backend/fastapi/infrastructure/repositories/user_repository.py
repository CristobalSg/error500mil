from typing import List, Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from domain.entities import UserCreate, UserUpdate
from domain.models import User, PasswordResetToken, PasswordResetAttempt
from infrastructure.auth import AuthService


class SQLUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: UserCreate) -> User:
        """Crear un nuevo usuario"""
        # Hash de la contraseña antes de guardar
        hashed_password = AuthService.get_password_hash(user.contrasena)

        # Crear el objeto User con los campos correctos
        db_user = User(
            nombre=user.nombre,
            email=user.email,
            pass_hash=hashed_password,
            rol=user.rol,
            activo=user.activo,
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: int, include_deleted: bool = False) -> Optional[User]:
        """
        Obtener usuario por ID con las relaciones cargadas.
        
        Args:
            user_id: ID del usuario
            include_deleted: Si True, incluye usuarios eliminados (soft delete)
        """
        query = (
            self.session.query(User)
            .options(joinedload(User.docente))
            .options(joinedload(User.estudiante))
            .options(joinedload(User.administrador))
            .filter(User.id == user_id)
        )
        
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        
        return query.first()

    def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """
        Obtener usuario por email con las relaciones cargadas.
        
        Args:
            email: Email del usuario
            include_deleted: Si True, incluye usuarios eliminados (soft delete)
        """
        query = (
            self.session.query(User)
            .options(joinedload(User.docente))
            .options(joinedload(User.estudiante))
            .options(joinedload(User.administrador))
            .filter(User.email == email)
        )
        
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        
        return query.first()

    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[User]:
        """
        Obtener todos los usuarios con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros
            include_deleted: Si True, incluye usuarios eliminados (soft delete)
        """
        query = self.session.query(User)
        
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        
        return query.offset(skip).limit(limit).all()

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Actualizar un usuario"""
        db_user = self.get_by_id(user_id)
        if db_user:
            update_data = user_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            self.session.commit()
            self.session.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        """
        Eliminar permanentemente un usuario (hard delete).
        
        ADVERTENCIA: Esta operación es irreversible.
        Se recomienda usar soft_delete() en su lugar.
        """
        db_user = self.get_by_id(user_id, include_deleted=True)
        if db_user:
            self.session.delete(db_user)
            self.session.commit()
            return True
        return False

    def soft_delete(self, user_id: int) -> Optional[User]:
        """
        Soft delete: marcar usuario como eliminado sin borrarlo físicamente.
        
        Args:
            user_id: ID del usuario a eliminar
        
        Returns:
            Usuario eliminado o None si no existe
        """
        db_user = self.get_by_id(user_id, include_deleted=False)
        if db_user:
            db_user.deleted_at = datetime.now(timezone.utc)
            db_user.activo = False  # También desactivar el usuario
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        return None

    def restore(self, user_id: int) -> Optional[User]:
        """
        Restaurar un usuario eliminado (soft delete).
        
        Args:
            user_id: ID del usuario a restaurar
        
        Returns:
            Usuario restaurado o None si no existe
        """
        db_user = self.get_by_id(user_id, include_deleted=True)
        if db_user and db_user.deleted_at is not None:
            db_user.deleted_at = None
            # No activamos automáticamente, el admin debe hacerlo explícitamente
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        return None

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuario con email y contraseña"""
        user = self.get_by_email(email)
        if user and AuthService.verify_password(password, user.pass_hash):
            return user
        return None

    def is_active(self, user: User) -> bool:
        """Verificar si el usuario está activo"""
        return user.activo

    def get_by_rol(self, rol: str, include_deleted: bool = False) -> List[User]:
        """
        Obtener usuarios por rol.
        
        Args:
            rol: Rol a filtrar
            include_deleted: Si True, incluye usuarios eliminados (soft delete)
        """
        query = self.session.query(User).filter(User.rol == rol)
        
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        
        return query.all()

    def count_users_by_role(self, include_deleted: bool = False) -> dict:
        """
        Contar usuarios agrupados por rol.
        
        Args:
            include_deleted: Si True, incluye usuarios eliminados (soft delete)
        
        Returns:
            Diccionario con el conteo por rol: {"docente": 5, "estudiante": 100, "administrador": 2}
        """
        from sqlalchemy import func
        
        query = self.session.query(
            User.rol,
            func.count(User.id).label('count')
        ).group_by(User.rol)
        
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))
        
        results = query.all()
        
        return {rol: count for rol, count in results}

    # ==================== RECUPERACIÓN DE CONTRASEÑA ====================

    def create_password_reset_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        request_ip: Optional[str] = None
    ) -> PasswordResetToken:
        """
        Crear un nuevo token de recuperación de contraseña.
        
        Args:
            user_id: ID del usuario
            token_hash: Hash del token (nunca el token en texto plano)
            expires_at: Fecha/hora de expiración
            request_ip: IP del solicitante (opcional)
        
        Returns:
            Token creado
        """
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            request_ip=request_ip
        )
        
        self.session.add(token)
        self.session.commit()
        self.session.refresh(token)
        
        return token

    def get_valid_password_reset_token(self, token_hash: str) -> Optional[PasswordResetToken]:
        """
        Buscar token válido (no usado y no expirado).
        
        Args:
            token_hash: Hash del token
        
        Returns:
            Token válido o None
        """
        now = datetime.now(timezone.utc)
        
        return self.session.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > now
            )
        ).first()

    def mark_password_reset_token_as_used(self, token: PasswordResetToken) -> PasswordResetToken:
        """
        Marcar token como usado.
        
        Args:
            token: Token a marcar
        
        Returns:
            Token actualizado
        """
        token.used = True
        token.used_at = datetime.now(timezone.utc)
        
        self.session.commit()
        self.session.refresh(token)
        
        return token

    def invalidate_user_password_reset_tokens(self, user_id: int) -> int:
        """
        Invalidar todos los tokens activos de un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Número de tokens invalidados
        """
        count = self.session.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used == False
            )
        ).update({"used": True, "used_at": datetime.now(timezone.utc)})
        
        self.session.commit()
        
        return count

    def update_user_password(self, user_id: int, new_password: str) -> Optional[User]:
        """
        Actualizar la contraseña de un usuario.
        
        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña (en texto plano, se hasheará)
        
        Returns:
            Usuario actualizado o None
        """
        user = self.get_by_id(user_id)
        if user:
            user.pass_hash = AuthService.get_password_hash(new_password)
            self.session.commit()
            self.session.refresh(user)
        return user

    def record_password_reset_attempt(
        self,
        email: str,
        ip_address: str,
        success: bool,
        failure_reason: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> PasswordResetAttempt:
        """
        Registrar un intento de recuperación de contraseña.
        
        Args:
            email: Email solicitado
            ip_address: IP del solicitante
            success: Si fue exitoso
            failure_reason: Razón de fallo (opcional)
            user_agent: User agent del navegador (opcional)
        
        Returns:
            Intento registrado
        """
        attempt = PasswordResetAttempt(
            email=email.lower(),
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent
        )
        
        self.session.add(attempt)
        self.session.commit()
        self.session.refresh(attempt)
        
        return attempt

    def get_recent_password_reset_attempts_by_email(
        self,
        email: str,
        minutes: int = 60
    ) -> List[PasswordResetAttempt]:
        """
        Obtener intentos recientes de recuperación por email.
        
        Args:
            email: Email a buscar
            minutes: Ventana de tiempo en minutos
        
        Returns:
            Lista de intentos
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        return self.session.query(PasswordResetAttempt).filter(
            and_(
                PasswordResetAttempt.email == email.lower(),
                PasswordResetAttempt.attempted_at > cutoff_time
            )
        ).order_by(PasswordResetAttempt.attempted_at.desc()).all()

    def get_recent_password_reset_attempts_by_ip(
        self,
        ip_address: str,
        minutes: int = 60
    ) -> List[PasswordResetAttempt]:
        """
        Obtener intentos recientes de recuperación por IP.
        
        Args:
            ip_address: IP a buscar
            minutes: Ventana de tiempo en minutos
        
        Returns:
            Lista de intentos
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        return self.session.query(PasswordResetAttempt).filter(
            and_(
                PasswordResetAttempt.ip_address == ip_address,
                PasswordResetAttempt.attempted_at > cutoff_time
            )
        ).order_by(PasswordResetAttempt.attempted_at.desc()).all()
