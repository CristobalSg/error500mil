"""
Casos de uso para recuperación de contraseñas.

Implementa la lógica de negocio para el sistema de recuperación de contraseñas
siguiendo las mejores prácticas de seguridad OWASP:
- Tokens seguros con tiempo de expiración
- Rate limiting por email e IP
- Prevención de enumeración de usuarios
- Logs de auditoría
- Protección contra fuerza bruta
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status

from domain.schemas import (
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
    PasswordResetResponseSchema,
    PasswordResetSuccessSchema,
    PasswordChangeSchema,
    PasswordChangeSuccessSchema
)
from domain.models import User
from infrastructure.repositories.user_repository import SQLUserRepository
from infrastructure.auth import AuthService

logger = logging.getLogger(__name__)


class PasswordResetUseCase:
    """
    Casos de uso para recuperación de contraseña.
    
    Características de seguridad:
    - Tokens criptográficamente seguros
    - Rate limiting estricto
    - Prevención de enumeración de usuarios
    - Auditoría completa
    - Tokens de un solo uso
    """
    
    # Configuración de seguridad
    TOKEN_LENGTH = 32  # bytes (64 caracteres hex)
    TOKEN_EXPIRY_HOURS = 1  # Tokens expiran en 1 hora
    MAX_ATTEMPTS_PER_EMAIL = 3  # Máximo de intentos por email en ventana de tiempo
    MAX_ATTEMPTS_PER_IP = 10  # Máximo de intentos por IP en ventana de tiempo
    RATE_LIMIT_WINDOW_MINUTES = 60  # Ventana de tiempo para rate limiting
    
    def __init__(self, user_repository: SQLUserRepository):
        self.user_repository = user_repository

    def request_password_reset(
        self,
        request_data: PasswordResetRequestSchema,
        client_ip: str,
        user_agent: Optional[str] = None
    ) -> PasswordResetResponseSchema:
        """
        Solicitar recuperación de contraseña.
        
        IMPORTANTE: Siempre retorna respuesta exitosa para prevenir
        enumeración de usuarios, independientemente de si el email existe.
        
        Args:
            request_data: Datos de la solicitud (email)
            client_ip: IP del cliente
            user_agent: User agent del cliente
        
        Returns:
            Respuesta genérica de éxito
        
        Raises:
            HTTPException: Si se excede el rate limit
        """
        email = request_data.email.lower()
        
        # 1. Verificar rate limiting por email
        email_attempts = self.user_repository.get_recent_password_reset_attempts_by_email(
            email, 
            self.RATE_LIMIT_WINDOW_MINUTES
        )
        
        if len(email_attempts) >= self.MAX_ATTEMPTS_PER_EMAIL:
            logger.warning(
                f"Rate limit excedido para email {email} "
                f"({len(email_attempts)} intentos en {self.RATE_LIMIT_WINDOW_MINUTES} minutos)"
            )
            # Registrar intento fallido
            self.user_repository.record_password_reset_attempt(
                email=email,
                ip_address=client_ip,
                success=False,
                failure_reason="rate_limit_email",
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Demasiados intentos para este email. Por favor, espera {self.RATE_LIMIT_WINDOW_MINUTES} minutos."
            )
        
        # 2. Verificar rate limiting por IP
        ip_attempts = self.user_repository.get_recent_password_reset_attempts_by_ip(
            client_ip,
            self.RATE_LIMIT_WINDOW_MINUTES
        )
        
        if len(ip_attempts) >= self.MAX_ATTEMPTS_PER_IP:
            logger.warning(
                f"Rate limit excedido para IP {client_ip} "
                f"({len(ip_attempts)} intentos en {self.RATE_LIMIT_WINDOW_MINUTES} minutos)"
            )
            # Registrar intento fallido
            self.user_repository.record_password_reset_attempt(
                email=email,
                ip_address=client_ip,
                success=False,
                failure_reason="rate_limit_ip",
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Demasiados intentos desde esta dirección IP. Por favor, espera {self.RATE_LIMIT_WINDOW_MINUTES} minutos."
            )
        
        # 3. Buscar usuario por email
        user = self.user_repository.get_by_email(email)
        
        if user:
            # Usuario existe - crear token real
            if not user.activo:
                # Usuario inactivo - registrar pero no crear token
                logger.info(f"Intento de recuperación para usuario inactivo: {email}")
                self.user_repository.record_password_reset_attempt(
                    email=email,
                    ip_address=client_ip,
                    success=False,
                    failure_reason="user_inactive",
                    user_agent=user_agent
                )
            else:
                # Usuario activo - procesar normalmente
                try:
                    # Invalidar tokens anteriores del usuario
                    self.user_repository.invalidate_user_password_reset_tokens(user.id)
                    
                    # Generar token seguro
                    token = secrets.token_urlsafe(self.TOKEN_LENGTH)
                    token_hash = self._hash_token(token)
                    
                    # Calcular expiración
                    expires_at = datetime.now(timezone.utc) + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
                    
                    # Guardar token en BD
                    self.user_repository.create_password_reset_token(
                        user_id=user.id,
                        token_hash=token_hash,
                        expires_at=expires_at,
                        request_ip=client_ip
                    )
                    
                    # Registrar intento exitoso
                    self.user_repository.record_password_reset_attempt(
                        email=email,
                        ip_address=client_ip,
                        success=True,
                        user_agent=user_agent
                    )
                    
                    # TODO: Enviar email con el token
                    # En desarrollo, logueamos el token (NUNCA en producción)
                    logger.info(f"Token de recuperación generado para {email}")
                    logger.debug(f"Token (SOLO DESARROLLO): {token}")
                    
                    # Aquí iría la lógica de envío de email
                    # self._send_password_reset_email(user.email, user.nombre, token)
                    
                except Exception as e:
                    logger.error(f"Error al crear token de recuperación: {str(e)}")
                    # Continuar para no revelar el error al usuario
        else:
            # Usuario no existe - registrar intento
            logger.info(f"Intento de recuperación para email no existente: {email}")
            self.user_repository.record_password_reset_attempt(
                email=email,
                ip_address=client_ip,
                success=False,
                failure_reason="user_not_found",
                user_agent=user_agent
            )
        
        # 4. SIEMPRE retornar respuesta exitosa (prevenir enumeración)
        return PasswordResetResponseSchema(
            mensaje="Si el email está registrado, recibirás un link para recuperar tu contraseña.",
            email=email
        )

    def confirm_password_reset(
        self,
        confirm_data: PasswordResetConfirmSchema,
        client_ip: str
    ) -> PasswordResetSuccessSchema:
        """
        Confirmar recuperación de contraseña con token y nueva contraseña.
        
        Args:
            confirm_data: Datos de confirmación (token y nueva contraseña)
            client_ip: IP del cliente
        
        Returns:
            Respuesta de éxito
        
        Raises:
            HTTPException: Si el token es inválido o expirado
        """
        token = confirm_data.token
        nueva_contrasena = confirm_data.nueva_contrasena
        
        # 1. Hash del token para buscarlo en BD
        token_hash = self._hash_token(token)
        
        # 2. Buscar token válido
        reset_token = self.user_repository.get_valid_password_reset_token(token_hash)
        
        if not reset_token:
            logger.warning(f"Token de recuperación inválido o expirado desde IP {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado. Por favor, solicita un nuevo link de recuperación."
            )
        
        # 3. Obtener usuario
        user = self.user_repository.get_by_id(reset_token.user_id)
        
        if not user:
            logger.error(f"Usuario no encontrado para token válido: {reset_token.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido."
            )
        
        if not user.activo:
            logger.warning(f"Intento de recuperación para usuario inactivo: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede restablecer la contraseña para este usuario."
            )
        
        try:
            # 4. Actualizar contraseña
            self.user_repository.update_user_password(user.id, nueva_contrasena)
            
            # 5. Marcar token como usado
            self.user_repository.mark_password_reset_token_as_used(reset_token)
            
            # 6. Invalidar cualquier otro token activo del usuario
            self.user_repository.invalidate_user_password_reset_tokens(user.id)
            
            logger.info(f"Contraseña restablecida exitosamente para usuario {user.email}")
            
            # TODO: Enviar email de confirmación
            # self._send_password_changed_notification(user.email, user.nombre)
            
            return PasswordResetSuccessSchema(
                mensaje="Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.",
                email=user.email
            )
            
        except Exception as e:
            logger.error(f"Error al restablecer contraseña: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al restablecer la contraseña. Por favor, intenta nuevamente."
            )

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Crear hash del token para almacenamiento seguro.
        
        Args:
            token: Token en texto plano
        
        Returns:
            Hash del token (SHA-256)
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def _send_password_reset_email(self, email: str, nombre: str, token: str):
        """
        Enviar email con link de recuperación.
        
        TODO: Implementar envío real de emails.
        Por ahora es un placeholder.
        
        Args:
            email: Email del destinatario
            nombre: Nombre del usuario
            token: Token de recuperación
        """
        # Construcción del link de recuperación
        # En producción, usar la URL real del frontend
        reset_link = f"https://tu-dominio.cl/reset-password?token={token}"
        
        logger.info(f"[EMAIL] Enviando link de recuperación a {email}")
        logger.debug(f"[EMAIL] Link: {reset_link}")
        
        # Aquí iría la integración con servicio de email (SendGrid, SES, etc.)
        pass

    def _send_password_changed_notification(self, email: str, nombre: str):
        """
        Enviar notificación de cambio de contraseña exitoso.
        
        TODO: Implementar envío real de emails.
        
        Args:
            email: Email del destinatario
            nombre: Nombre del usuario
        """
        logger.info(f"[EMAIL] Enviando notificación de cambio de contraseña a {email}")
        
        # Aquí iría la integración con servicio de email
        pass

    def change_password(
        self,
        user: User,
        change_data: PasswordChangeSchema,
        client_ip: str
    ) -> PasswordChangeSuccessSchema:
        """
        Cambiar contraseña de usuario autenticado.
        
        Args:
            user: Usuario autenticado actual
            change_data: Datos del cambio (contraseña actual y nueva)
            client_ip: IP del cliente
        
        Returns:
            Respuesta de éxito
        
        Raises:
            HTTPException: Si la contraseña actual es incorrecta
        """
        # 1. Verificar que la contraseña actual sea correcta
        if not AuthService.verify_password(change_data.contrasena_actual, user.pass_hash):
            logger.warning(
                f"Intento fallido de cambio de contraseña para {user.email} "
                f"desde IP {client_ip} - Contraseña actual incorrecta"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta."
            )
        
        # 2. Verificar que el usuario esté activo
        if not user.activo:
            logger.warning(f"Intento de cambio de contraseña para usuario inactivo: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar la contraseña para este usuario."
            )
        
        try:
            # 3. Actualizar contraseña
            self.user_repository.update_user_password(user.id, change_data.contrasena_nueva)
            
            # 4. Invalidar todos los tokens de recuperación (si existen)
            self.user_repository.invalidate_user_password_reset_tokens(user.id)
            
            logger.info(
                f"Contraseña cambiada exitosamente para usuario {user.email} "
                f"desde IP {client_ip}"
            )
            
            # TODO: Enviar email de notificación
            # self._send_password_changed_notification(user.email, user.nombre)
            
            return PasswordChangeSuccessSchema(
                mensaje="Contraseña cambiada exitosamente.",
                email=user.email
            )
            
        except Exception as e:
            logger.error(f"Error al cambiar contraseña para {user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al cambiar la contraseña. Por favor, intenta nuevamente."
            )
