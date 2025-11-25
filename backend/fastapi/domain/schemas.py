"""
Schemas de validación estricta para prevenir OWASP A03: Injection
=================================================================

Este módulo define schemas Pydantic con validaciones estrictas para mitigar
riesgos de inyección incluyendo:
- SQL Injection
- NoSQL Injection
- Command Injection
- LDAP Injection
- XPath Injection
- Path Traversal

Estrategias de mitigación:
1. Validación de tipos estricta
2. Listas blancas de valores permitidos
3. Validación de patrones con regex
4. Sanitización de entrada
5. Validación de rangos
6. Prevención de caracteres peligrosos
7. Normalización de datos
"""

import re
from datetime import date, datetime, time
from enum import Enum
from typing import List, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    conint,
    constr,
    field_validator,
    model_validator,
)

# ============================================================================
# ENUMERACIONES - Listas blancas de valores permitidos
# ============================================================================


class RolEnum(str, Enum):
    """Roles permitidos en el sistema - Lista blanca estricta"""

    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"
    ADMINISTRADOR = "administrador"


class TipoRestriccionEnum(str, Enum):
    """Tipos de restricciones permitidas - Lista blanca estricta"""

    HORARIO = "horario"
    AULA = "aula"
    MATERIA = "materia"
    PERIODO = "periodo"
    DISPONIBILIDAD = "disponibilidad"


class TipoSalaEnum(str, Enum):
    """Tipos de salas permitidas - Lista blanca estricta"""

    AULA = "aula"
    LABORATORIO = "laboratorio"
    AUDITORIO = "auditorio"
    TALLER = "taller"
    SALA_CONFERENCIAS = "sala_conferencias"


class EstadoClaseEnum(str, Enum):
    """Estados de clase permitidos - Lista blanca estricta"""

    PROGRAMADA = "programada"
    EN_CURSO = "en_curso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"
    SUSPENDIDA = "suspendida"


class DiaSemanaEnum(int, Enum):
    """Días de la semana - Lista blanca estricta"""

    DOMINGO = 0
    LUNES = 1
    MARTES = 2
    MIERCOLES = 3
    JUEVES = 4
    VIERNES = 5
    SABADO = 6


# ============================================================================
# VALIDADORES PERSONALIZADOS - Prevención de inyección
# ============================================================================


class BaseSecureValidator:
    """Clase base con validadores seguros reutilizables"""

    # Patrones peligrosos que podrían indicar ataques de inyección
    DANGEROUS_PATTERNS = [
        r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bCREATE\b|\bALTER\b)",  # SQL
        r"(\$\{|\$\(|`|\beval\b|\bexec\b)",  # Command injection
        r"(<script|<iframe|javascript:|onerror=|onload=)",  # XSS
        r"(\.\./|\.\.\\|%2e%2e)",  # Path traversal
        r"(\|\||&&|;|\||&)",  # Command chaining
        r"(\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4})",  # Encoded characters
        r"(\bUNION\b|\bJOIN\b|\bWHERE\b|\bHAVING\b)",  # SQL advanced
        r"(--|\#|\/\*|\*\/)",  # SQL comments
        r"(\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)",  # SQL tautology
    ]

    # Caracteres permitidos en códigos alfanuméricos
    ALPHANUMERIC_PATTERN = re.compile(r"^[A-Z0-9\-]+$")

    # Caracteres permitidos en nombres (letras, espacios, acentos)
    NAME_PATTERN = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$")

    # Caracteres permitidos en descripciones (más permisivo pero controlado)
    DESCRIPTION_PATTERN = re.compile(r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,;:()\-_¿?¡!']+$")

    @classmethod
    def validate_no_injection(cls, value: str, field_name: str = "campo") -> str:
        """
        Valida que el valor no contenga patrones de inyección

        Args:
            value: Valor a validar
            field_name: Nombre del campo (para mensajes de error)

        Returns:
            str: Valor validado

        Raises:
            ValueError: Si se detectan patrones peligrosos
        """
        if not value:
            return value

        # Detectar patrones peligrosos
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(
                    f"El {field_name} contiene caracteres o patrones no permitidos. "
                    f"Por seguridad, evita usar caracteres especiales como: "
                    f"< > $ ` | & ; -- /* */"
                )

        return value

    @classmethod
    def validate_alphanumeric_code(cls, value: str, field_name: str = "código") -> str:
        """
        Valida códigos alfanuméricos estrictos (solo A-Z, 0-9, -)

        Args:
            value: Código a validar
            field_name: Nombre del campo

        Returns:
            str: Código validado y normalizado

        Raises:
            ValueError: Si el código contiene caracteres no permitidos
        """
        value = value.strip().upper()

        # Validar que solo contenga caracteres permitidos (ahora que está en mayúsculas)
        if not re.match(r"^[A-Z0-9\-]+$", value):
            raise ValueError(
                f"El {field_name} solo puede contener letras (A-Z), " f"números (0-9) y guiones (-)"
            )

        # Validación adicional contra inyección
        cls.validate_no_injection(value, field_name)

        return value

    @classmethod
    def validate_name(cls, value: str, field_name: str = "nombre") -> str:
        """
        Valida nombres (solo letras y espacios)

        Args:
            value: Nombre a validar
            field_name: Nombre del campo

        Returns:
            str: Nombre validado y normalizado

        Raises:
            ValueError: Si el nombre contiene caracteres no permitidos
        """
        value = value.strip()

        if not cls.NAME_PATTERN.match(value):
            raise ValueError(f"El {field_name} solo puede contener letras y espacios")

        # Validación adicional contra inyección
        cls.validate_no_injection(value, field_name)

        return value

    @classmethod
    def validate_description(
        cls, value: Optional[str], field_name: str = "descripción"
    ) -> Optional[str]:
        """
        Valida descripciones (caracteres controlados)

        Args:
            value: Descripción a validar
            field_name: Nombre del campo

        Returns:
            Optional[str]: Descripción validada

        Raises:
            ValueError: Si la descripción contiene caracteres peligrosos
        """
        if not value or not value.strip():
            return None

        value = value.strip()

        if not cls.DESCRIPTION_PATTERN.match(value):
            raise ValueError(
                f"La {field_name} contiene caracteres no permitidos. "
                f"Solo se permiten letras, números, espacios y puntuación básica (.,;:()-_¿?¡!)"
            )

        # Validación adicional contra inyección
        cls.validate_no_injection(value, field_name)

        return value

    @classmethod
    def validate_positive_integer(cls, value: int, field_name: str = "valor") -> int:
        """
        Valida que el entero sea positivo (previene valores negativos maliciosos)

        Args:
            value: Entero a validar
            field_name: Nombre del campo

        Returns:
            int: Valor validado

        Raises:
            ValueError: Si el valor no es positivo
        """
        if value <= 0:
            raise ValueError(f"El {field_name} debe ser mayor a 0")

        return value

    @classmethod
    def validate_range(
        cls, value: int, min_val: int, max_val: int, field_name: str = "valor"
    ) -> int:
        """
        Valida que el valor esté en un rango específico

        Args:
            value: Valor a validar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            field_name: Nombre del campo

        Returns:
            int: Valor validado

        Raises:
            ValueError: Si el valor está fuera del rango
        """
        if not min_val <= value <= max_val:
            raise ValueError(f"El {field_name} debe estar entre {min_val} y {max_val}")

        return value


# ============================================================================
# SCHEMAS DE USUARIO - Con validaciones anti-inyección
# ============================================================================


class UserSecureBase(BaseModel, BaseSecureValidator):
    """Schema base de usuario con validaciones de seguridad"""

    nombre: constr(
        strip_whitespace=True, min_length=2, max_length=100, pattern=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$"
    ) = Field(
        ...,
        description="Nombre completo del usuario (solo letras y espacios)",
        examples=["Juan Pérez", "María González"],
    )

    email: EmailStr = Field(
        ..., description="Correo electrónico válido", examples=["usuario@ejemplo.cl"]
    )

    rol: RolEnum = Field(..., description="Rol del usuario en el sistema")

    activo: bool = Field(default=True, description="Indica si el usuario está activo")

    @field_validator("nombre")
    @classmethod
    def validate_nombre_secure(cls, v: str) -> str:
        """Validación adicional del nombre contra inyección"""
        return cls.validate_name(v, "nombre")

    @field_validator("email")
    @classmethod
    def validate_email_secure(cls, v: str) -> str:
        """Validación adicional del email contra inyección"""
        # EmailStr ya valida formato, pero agregamos validación anti-inyección
        cls.validate_no_injection(v, "email")

        # Validar longitud máxima del email
        if len(v) > 254:  # RFC 5321
            raise ValueError("El email es demasiado largo (máximo 254 caracteres)")

        # Validar dominio (parte después del @)
        domain = v.split("@")[1]
        if len(domain) > 253:
            raise ValueError("El dominio del email es demasiado largo")

        return v.lower()


class UserSecureCreate(UserSecureBase):
    """Schema para creación de usuario con validación de contraseña segura y datos específicos del rol"""

    contrasena: constr(min_length=12, max_length=128) = Field(
        ...,
        description="Contraseña segura (mín. 12 caracteres, mayúsculas, minúsculas, números y especiales)",
    )

    # Campos específicos por rol (opcionales, pero se validan según el rol)
    departamento: Optional[constr(strip_whitespace=True, min_length=1, max_length=100, to_upper=True)] = Field(
        None, description="Departamento (OBLIGATORIO para docentes)"
    )
    
    permisos: Optional[constr(strip_whitespace=True, min_length=1, max_length=500)] = Field(
        None, description="Permisos (opcional para administradores)"
    )

    @model_validator(mode="after")
    def validate_rol_specific_fields(self):
        """Validar que los campos específicos del rol estén presentes según corresponda"""
        if self.rol == RolEnum.DOCENTE:
            if not self.departamento:
                raise ValueError("El campo 'departamento' es obligatorio para usuarios con rol 'docente'")
            # Validar departamento
            BaseSecureValidator.validate_no_injection(self.departamento, "departamento")
            BaseSecureValidator.validate_name(self.departamento, "departamento")
        
        if self.permisos:
            # Validar permisos si se proporcionan
            BaseSecureValidator.validate_no_injection(self.permisos, "permisos")
        
        return self

    @field_validator("contrasena")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validación exhaustiva de fortaleza de contraseña
        Previene contraseñas débiles que facilitan ataques
        """
        # Longitud mínima
        if len(v) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres")

        # Longitud máxima (prevenir DoS)
        if len(v) > 128:
            raise ValueError("La contraseña es demasiado larga (máximo 128 caracteres)")

        # Al menos una mayúscula
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")

        # Al menos una minúscula
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")

        # Al menos un número
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")

        # Al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/~`]', v):
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial "
                '(!@#$%^&*(),.?":{}|<>_-+=[]\\;/~`)'
            )

        # Prevenir contraseñas con caracteres de control (posible inyección)
        if re.search(r"[\x00-\x1F\x7F]", v):
            raise ValueError("La contraseña contiene caracteres no permitidos")

        # Prevenir caracteres repetidos excesivos
        if len(set(v)) < 6:
            raise ValueError("La contraseña debe tener mayor variedad de caracteres")

        # Prevenir secuencias simples consecutivas (3+ caracteres)
        sequences = [
            "abc",
            "bcd",
            "cde",
            "def",
            "123",
            "234",
            "345",
            "456",
            "qwe",
            "wer",
            "ert",
            "asd",
            "sdf",
            "dfg",
            "zxc",
            "xcv",
            "cvb",
        ]
        v_lower = v.lower()
        has_sequence = False
        for seq in sequences:
            if seq in v_lower or seq[::-1] in v_lower:
                has_sequence = True
                break
        # Solo rechazar si tiene secuencias Y es una contraseña corta/simple
        if has_sequence and len(v) < 16:
            # Verificar si es muy simple
            if sum(1 for c in v if c.isdigit()) < 4 or sum(1 for c in v if c.isalpha()) < 4:
                raise ValueError("La contraseña no debe contener secuencias simples evidentes")

        return v


class UserSecureLogin(BaseModel, BaseSecureValidator):
    """Schema para login con validaciones de seguridad"""

    email: EmailStr = Field(..., description="Correo electrónico del usuario")

    contrasena: constr(min_length=8, max_length=128) = Field(
        ..., description="Contraseña del usuario"
    )

    @field_validator("email")
    @classmethod
    def validate_email_login(cls, v: str) -> str:
        """Validación del email en login"""
        cls.validate_no_injection(v, "email")

        if len(v) > 254:
            raise ValueError("Email inválido")

        return v.lower()

    @field_validator("contrasena")
    @classmethod
    def validate_password_login(cls, v: str) -> str:
        """Validación básica de contraseña en login"""
        # No revelamos detalles específicos en login (prevenir enumeración)
        if len(v) < 8 or len(v) > 128:
            raise ValueError("Credenciales inválidas")

        # Prevenir caracteres de control
        if re.search(r"[\x00-\x1F\x7F]", v):
            raise ValueError("Credenciales inválidas")

        return v


# ============================================================================
# SCHEMAS DE CÓDIGO - Validación estricta de códigos alfanuméricos
# ============================================================================


class CodigoSeguroMixin(BaseSecureValidator):
    """Mixin para validación de códigos seguros"""

    @field_validator("codigo")
    @classmethod
    def validate_codigo_seguro(cls, v: str) -> str:
        """Validación estricta de códigos"""
        return cls.validate_alphanumeric_code(v, "código")


class AsignaturaSecureBase(BaseModel, CodigoSeguroMixin):
    """Schema de asignatura con validaciones de seguridad"""

    codigo: constr(strip_whitespace=True, to_upper=True, min_length=1, max_length=100) = Field(
        ...,
        description="Código único de la asignatura (A-Z, 0-9, -)",
        examples=["MAT-101", "FIS-201", "COMP-SCI-301"],
    )

    nombre: constr(strip_whitespace=True, min_length=2, max_length=100) = Field(
        ..., description="Nombre de la asignatura", examples=["Matemáticas I", "Física II"]
    )

    horas_presenciales: conint(ge=0) = Field(
        ..., description="Horas presenciales semanales", examples=[2, 3, 4]
    )

    horas_mixtas: conint(ge=0) = Field(
        ..., description="Horas mixtas semanales", examples=[1, 2]
    )

    horas_autonomas: conint(ge=0) = Field(
        ..., description="Horas autónomas semanales", examples=[2, 3, 5]
    )

    cantidad_creditos: conint(ge=1, le=30) = Field(
        ..., description="Número de créditos (1-30)", examples=[3, 4, 6]
    )

    semestre: conint(ge=1, le=12) = Field(
        ..., description="Semestre recomendado (1-12)", examples=[1, 2, 3]
    )

    @field_validator("nombre")
    @classmethod
    def validate_nombre_asignatura(cls, v: str) -> str:
        """Validación del nombre de asignatura"""
        return cls.validate_name(v, "nombre de asignatura")


class SeccionSecureBase(BaseModel, CodigoSeguroMixin):
    """Schema de sección con validaciones de seguridad"""

    codigo: constr(strip_whitespace=True, min_length=1, max_length=100) = Field(
        ..., description="Nombre del grupo (ej: '1 sección 1', '5 mención 1')"
    )

    anio_academico: conint(ge=1, le=5) = Field(
        ..., description="Año académico (1-5)", examples=[1, 2, 3, 4, 5]
    )

    semestre: Literal[1, 2] = Field(..., description="Semestre (1 o 2)", examples=[1, 2])

    tipo_grupo: constr(strip_whitespace=True, to_lower=True, min_length=1, max_length=20) = Field(
        ..., description="Tipo de grupo: seccion, mencion, base", examples=["seccion", "mencion", "base"]
    )

    numero_estudiantes: conint(ge=1, le=500) = Field(
        ..., description="Número de estudiantes en el grupo (1-500)", examples=[30, 40, 50]
    )

    cupos: Optional[conint(ge=1, le=500)] = Field(
        None, description="Número de cupos disponibles (1-500)"
    )

    @field_validator("tipo_grupo")
    @classmethod
    def validate_tipo_grupo(cls, v: str) -> str:
        """Validar que el tipo_grupo sea válido"""
        valid_tipos = ["seccion", "mencion", "base"]
        if v not in valid_tipos:
            raise ValueError(f"tipo_grupo debe ser uno de: {', '.join(valid_tipos)}")
        return v


class SalaSecureBase(BaseModel, CodigoSeguroMixin):
    """Schema de sala con validaciones de seguridad"""

    codigo: constr(strip_whitespace=True, to_upper=True, min_length=1, max_length=100) = Field(
        ..., description="Código único de la sala", examples=["A-101", "LAB-201", "AUD-PRINCIPAL"]
    )

    capacidad: conint(ge=1, le=500) = Field(
        ..., description="Capacidad de la sala (1-500)", examples=[30, 50, 100]
    )

    tipo: TipoSalaEnum = Field(..., description="Tipo de sala")

    disponible: bool = Field(default=True, description="Indica si la sala está disponible")

    equipamiento: Optional[constr(max_length=500)] = Field(
        None, description="Descripción del equipamiento de la sala"
    )

    @field_validator("equipamiento")
    @classmethod
    def validate_equipamiento(cls, v: Optional[str]) -> Optional[str]:
        """Validación del equipamiento"""
        return cls.validate_description(v, "equipamiento")


# ============================================================================
# SCHEMAS DE HORARIO - Validación de tiempos
# ============================================================================


class HorarioSecureMixin(BaseSecureValidator):
    """Mixin para validación de horarios"""

    @model_validator(mode="after")
    def validate_time_range(self):
        """Valida que la hora de fin sea posterior a la hora de inicio"""
        if hasattr(self, "hora_fin") and hasattr(self, "hora_inicio"):
            if self.hora_fin is not None and self.hora_inicio is not None:
                if self.hora_fin <= self.hora_inicio:
                    raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return self


class BloqueSecureBase(BaseModel, HorarioSecureMixin):
    """Schema de bloque horario con validaciones de seguridad"""

    dia_semana: DiaSemanaEnum = Field(..., description="Día de la semana (0=Domingo, 6=Sábado)")

    hora_inicio: time = Field(
        ..., description="Hora de inicio del bloque", examples=["08:00:00", "14:30:00"]
    )

    hora_fin: time = Field(
        ..., description="Hora de fin del bloque", examples=["09:30:00", "16:00:00"]
    )

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def validate_business_hours(cls, v: time) -> time:
        """Valida que las horas estén en horario razonable (6:00 - 23:00)"""
        if not (time(8, 0) <= v <= time(21, 0)):
            raise ValueError("Las horas deben estar entre 08:00 y 21:00")
        return v


class RestriccionHorarioSecureBase(BaseModel, HorarioSecureMixin):
    """Schema de restricción de horario con validaciones de seguridad"""

    dia_semana: DiaSemanaEnum = Field(..., description="Día de la semana")

    hora_inicio: time = Field(..., description="Hora de inicio de la restricción")

    hora_fin: time = Field(..., description="Hora de fin de la restricción")

    disponible: bool = Field(
        ..., description="Indica si el docente está disponible en este horario"
    )

    descripcion: Optional[constr(max_length=255)] = Field(
        None, description="Descripción de la restricción"
    )

    activa: bool = Field(default=True, description="Indica si la restricción está activa")

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion_restriccion(cls, v: Optional[str]) -> Optional[str]:
        """Validación de descripción"""
        return cls.validate_description(v, "descripción")


# ============================================================================
# SCHEMAS DE RESTRICCIÓN - Validación de restricciones generales
# ============================================================================


class RestriccionSecureBase(BaseModel, BaseSecureValidator):
    """Schema de restricción con validaciones de seguridad"""

    tipo: TipoRestriccionEnum = Field(..., description="Tipo de restricción")

    valor: constr(strip_whitespace=True, min_length=1, max_length=255) = Field(
        ..., description="Valor de la restricción"
    )

    prioridad: conint(ge=1, le=10) = Field(
        ..., description="Prioridad de la restricción (1-10)", examples=[1, 5, 10]
    )

    restriccion_blanda: bool = Field(
        default=False, description="Indica si es una restricción blanda (puede violarse)"
    )

    restriccion_dura: bool = Field(
        default=False, description="Indica si es una restricción dura (no puede violarse)"
    )

    activa: bool = Field(default=True, description="Indica si la restricción está activa")

    @field_validator("valor")
    @classmethod
    def validate_valor_restriccion(cls, v: str) -> str:
        """Validación del valor de restricción"""
        return cls.validate_description(v, "valor")

    @model_validator(mode="after")
    def validate_restriccion_type(self):
        """Valida que al menos una sea blanda o dura"""
        if not self.restriccion_blanda and not self.restriccion_dura:
            raise ValueError("La restricción debe ser blanda o dura (o ambas)")
        return self


# ============================================================================
# SCHEMAS DE INFRAESTRUCTURA - Campus y Edificios
# ============================================================================


class CampusSecureBase(BaseModel, BaseSecureValidator):
    """Schema de campus con validaciones de seguridad"""

    nombre: constr(strip_whitespace=True, min_length=2, max_length=100) = Field(
        ..., description="Nombre del campus", examples=["Campus Central", "Campus Norte"]
    )

    direccion: Optional[constr(max_length=200)] = Field(None, description="Dirección del campus")

    @field_validator("nombre")
    @classmethod
    def validate_nombre_campus(cls, v: str) -> str:
        """Validación del nombre de campus"""
        return cls.validate_name(v, "nombre del campus")

    @field_validator("direccion")
    @classmethod
    def validate_direccion(cls, v: Optional[str]) -> Optional[str]:
        """Validación de dirección"""
        return cls.validate_description(v, "dirección")


class EdificioSecureBase(BaseModel, BaseSecureValidator):
    """Schema de edificio con validaciones de seguridad"""

    nombre: constr(strip_whitespace=True, min_length=2, max_length=100) = Field(
        ..., description="Nombre del edificio", examples=["Edificio A", "Torre Norte", "Pabellón 1"]
    )

    pisos: Optional[conint(ge=1, le=50)] = Field(
        None, description="Número de pisos del edificio (1-50)"
    )

    @field_validator("nombre")
    @classmethod
    def validate_nombre_edificio(cls, v: str) -> str:
        """Validación del nombre de edificio"""
        return cls.validate_name(v, "nombre del edificio")


# ============================================================================
# SCHEMAS DE CLASE - Estado y relaciones
# ============================================================================


class ClaseSecureBase(BaseModel, BaseSecureValidator):
    """Schema de clase con validaciones de seguridad"""

    estado: EstadoClaseEnum = Field(..., description="Estado de la clase")


# ============================================================================
# SCHEMAS DE CREACIÓN - Con IDs validados
# ============================================================================


class IDPositivoMixin(BaseSecureValidator):
    """Mixin para validación de IDs positivos"""

    @classmethod
    def validate_id_field(cls, v: int, field_name: str) -> int:
        """Valida que el ID sea positivo"""
        return cls.validate_positive_integer(v, field_name)


class AsignaturaSecureCreate(AsignaturaSecureBase):
    """Schema para creación de asignatura"""

    pass


class SeccionSecureCreate(SeccionSecureBase, IDPositivoMixin):
    """Schema para creación de sección"""

    asignatura_id: conint(gt=0) = Field(..., description="ID de la asignatura asociada")

    @field_validator("asignatura_id")
    @classmethod
    def validate_asignatura_id(cls, v: int) -> int:
        """Validación de ID de asignatura"""
        return cls.validate_id_field(v, "ID de asignatura")


class SalaSecureCreate(SalaSecureBase, IDPositivoMixin):
    """Schema para creación de sala"""

    edificio_id: conint(gt=0) = Field(..., description="ID del edificio asociado")

    @field_validator("edificio_id")
    @classmethod
    def validate_edificio_id(cls, v: int) -> int:
        """Validación de ID de edificio"""
        return cls.validate_id_field(v, "ID de edificio")


class BloqueSecureCreate(BloqueSecureBase):
    """Schema para creación de bloque"""

    pass


class RestriccionSecureCreate(RestriccionSecureBase, IDPositivoMixin):
    """
    Schema para creación de restricción.
    
    IMPORTANTE: Usa user_id (no docente_id) para consistencia con API de docentes.
    """

    user_id: conint(gt=0) = Field(..., description="ID del usuario docente (user_id, no docente_id)")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validación de ID de usuario docente"""
        return cls.validate_id_field(v, "ID de usuario docente")


class RestriccionHorarioSecureCreate(RestriccionHorarioSecureBase, IDPositivoMixin):
    """
    Schema para creación de restricción de horario.
    
    IMPORTANTE: Usa user_id (no docente_id) para consistencia con API de docentes.
    """

    user_id: conint(gt=0) = Field(..., description="ID del usuario docente (user_id, no docente_id)")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validación de ID de usuario docente"""
        return cls.validate_id_field(v, "ID de usuario docente")


class CampusSecureCreate(CampusSecureBase):
    """Schema para creación de campus"""

    pass


class EdificioSecureCreate(EdificioSecureBase, IDPositivoMixin):
    """Schema para creación de edificio"""

    campus_id: conint(gt=0) = Field(..., description="ID del campus asociado")

    @field_validator("campus_id")
    @classmethod
    def validate_campus_id(cls, v: int) -> int:
        """Validación de ID de campus"""
        return cls.validate_id_field(v, "ID de campus")


class ClaseSecureCreate(ClaseSecureBase, IDPositivoMixin):
    """Schema para creación de clase"""

    seccion_id: conint(gt=0) = Field(..., description="ID de la sección")

    docente_id: conint(gt=0) = Field(..., description="ID del docente (user_id del docente)")

    sala_id: conint(gt=0) = Field(..., description="ID de la sala")

    bloque_id: conint(gt=0) = Field(..., description="ID del bloque horario")

    @field_validator("seccion_id")
    @classmethod
    def validate_seccion_id(cls, v: int) -> int:
        """Validación de ID de sección"""
        return cls.validate_id_field(v, "ID de sección")

    @field_validator("docente_id")
    @classmethod
    def validate_docente_id(cls, v: int) -> int:
        """Validación de ID de docente"""
        return cls.validate_id_field(v, "ID de docente")

    @field_validator("sala_id")
    @classmethod
    def validate_sala_id(cls, v: int) -> int:
        """Validación de ID de sala"""
        return cls.validate_id_field(v, "ID de sala")

    @field_validator("bloque_id")
    @classmethod
    def validate_bloque_id(cls, v: int) -> int:
        """Validación de ID de bloque"""
        return cls.validate_id_field(v, "ID de bloque")


# ==========================================
# SCHEMAS SEGUROS PARA DOCENTE
# ==========================================


class DocenteSecureBase(BaseModel, BaseSecureValidator):
    """Schema base para docente con validaciones de seguridad"""

    departamento: Optional[
        constr(strip_whitespace=True, min_length=1, max_length=100, to_upper=True)
    ] = Field(None, description="Departamento del docente (validado contra inyección)")

    @field_validator("departamento")
    @classmethod
    def validate_departamento(cls, v: Optional[str]) -> Optional[str]:
        """Validar departamento del docente"""
        if v is None:
            return v

        # Validar contra inyecciones
        cls.validate_no_injection(v, "departamento")

        # Validar nombre válido (letras, espacios, guiones, tildes)
        cls.validate_name(v, "departamento")

        return v

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class DocenteSecureCreate(DocenteSecureBase, IDPositivoMixin):
    """Schema para creación de docente con validaciones anti-inyección"""

    user_id: conint(gt=0) = Field(..., description="ID del usuario asociado al docente")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validación de ID de usuario"""
        return cls.validate_id_field(v, "ID de usuario")


class EstudianteSecureBase(BaseModel, BaseSecureValidator):
    """
    Schema base para estudiante con validaciones anti-inyección.
    La matrícula se genera automáticamente, no se requiere en la creación.
    """
    pass


class EstudianteSecureCreate(EstudianteSecureBase, IDPositivoMixin):
    """
    Schema para creación de estudiante con validaciones anti-inyección.
    La matrícula se genera automáticamente basada en el año y el user_id.
    """
    user_id: conint(gt=0) = Field(..., description="ID del usuario asociado al estudiante")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validación de ID de usuario"""
        return cls.validate_id_field(v, "ID de usuario")


class AdministradorSecureBase(BaseModel, BaseSecureValidator):
    """Schema base para administrador con validaciones anti-inyección"""

    permisos: Optional[constr(strip_whitespace=True, min_length=1, max_length=500)] = Field(
        None, description="Permisos del administrador"
    )

    @field_validator("permisos")
    @classmethod
    def validate_permisos(cls, v: Optional[str]) -> Optional[str]:
        """Validar permisos contra inyecciones"""
        if v is None:
            return v

        # Validar contra inyecciones
        cls.validate_no_injection(v, "permisos")

        return v

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class AdministradorSecureCreate(AdministradorSecureBase, IDPositivoMixin):
    """Schema para creación de administrador con validaciones anti-inyección"""

    user_id: conint(gt=0) = Field(..., description="ID del usuario asociado al administrador")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validación de ID de usuario"""
        return cls.validate_id_field(v, "ID de usuario")


# ============================================================================
# SCHEMAS DE EVENTO - Validación de eventos de docentes
# ============================================================================


class EventoSecureBase(BaseModel, HorarioSecureMixin, BaseSecureValidator):
    """Schema base de evento con validaciones de seguridad"""

    nombre: constr(strip_whitespace=True, min_length=2, max_length=100) = Field(
        ..., description="Nombre del evento", examples=["Reunión de Profesores", "Consejo de Departamento"]
    )

    descripcion: Optional[constr(max_length=500)] = Field(
        None, description="Descripción del evento"
    )

    fecha: date = Field(
        ..., description="Fecha del evento", examples=["2025-11-20", "2025-12-15"]
    )

    hora_inicio: time = Field(
        ..., description="Hora de inicio del evento", examples=["09:00:00", "14:30:00"]
    )

    hora_cierre: time = Field(
        ..., description="Hora de cierre del evento", examples=["11:00:00", "16:00:00"]
    )

    activo: bool = Field(default=True, description="Indica si el evento está activo")
    
    clase_id: Optional[conint(gt=0)] = Field(
        None, 
        description="ID de la clase asociada (opcional: NULL para eventos personales/departamento, ID para eventos de clase)"
    )

    @field_validator("nombre")
    @classmethod
    def validate_nombre_evento(cls, v: str) -> str:
        """Validación del nombre del evento"""
        return cls.validate_name(v, "nombre del evento")

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion_evento(cls, v: Optional[str]) -> Optional[str]:
        """Validación de descripción"""
        return cls.validate_description(v, "descripción")

    @field_validator("hora_inicio", "hora_cierre")
    @classmethod
    def validate_business_hours(cls, v: time) -> time:
        """Valida que las horas estén en horario razonable (8:00 - 21:00)"""
        if not (time(8, 0) <= v <= time(21, 0)):
            raise ValueError("Las horas deben estar entre 08:00 y 21:00")
        return v
    
    @field_validator("clase_id")
    @classmethod
    def validate_clase_id(cls, v: Optional[int]) -> Optional[int]:
        """Validación de ID de clase"""
        if v is not None:
            return cls.validate_id_field(v, "ID de clase")
        return v

    @model_validator(mode="after")
    def validate_time_range(self):
        """Valida que la hora de cierre sea posterior a la hora de inicio"""
        if self.hora_cierre <= self.hora_inicio:
            raise ValueError("La hora de cierre debe ser posterior a la hora de inicio")
        return self


class EventoSecureCreate(EventoSecureBase, IDPositivoMixin):
    """
    Schema para creación de evento.
    
    IMPORTANTE: Usa user_id (no docente_id) para consistencia con API de docentes.
    """

    user_id: conint(gt=0) = Field(..., description="ID del usuario docente (user_id, no docente_id)")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validación de ID de usuario docente"""
        return cls.validate_id_field(v, "ID de usuario docente")


class EventoSecurePatch(BaseModel):
    """Schema para actualización parcial de evento"""

    nombre: Optional[constr(strip_whitespace=True, min_length=2, max_length=100)] = None
    descripcion: Optional[constr(max_length=500)] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_cierre: Optional[time] = None
    activo: Optional[bool] = None
    clase_id: Optional[conint(gt=0)] = Field(None, description="ID de la clase asociada")

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, v: Optional[str]) -> Optional[str]:
        """Validar nombre"""
        if v is None:
            return v
        BaseSecureValidator.validate_name(v, "nombre del evento")
        return v

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion(cls, v: Optional[str]) -> Optional[str]:
        """Validar descripción"""
        if v is None:
            return v
        return BaseSecureValidator.validate_description(v, "descripción")

    @field_validator("hora_inicio", "hora_cierre")
    @classmethod
    def validate_hours(cls, v: Optional[time]) -> Optional[time]:
        """Validar horas"""
        if v is not None and not (time(8, 0) <= v <= time(21, 0)):
            raise ValueError("Las horas deben estar entre 08:00 y 21:00")
        return v

    @model_validator(mode="after")
    def validate_time_range(self):
        """Validar rango de tiempo"""
        if self.hora_cierre is not None and self.hora_inicio is not None:
            if self.hora_cierre <= self.hora_inicio:
                raise ValueError("La hora de cierre debe ser posterior a la hora de inicio")
        return self


# ============================================================================
# SCHEMAS DE ACTUALIZACIÓN PARCIAL (PATCH) - Todos los campos opcionales
# ============================================================================


class AsignaturaSecurePatch(BaseModel):
    """Schema para actualización parcial de asignatura"""

    codigo: Optional[
        constr(
            strip_whitespace=True,
            to_upper=True,
            min_length=1,
            max_length=100,
            pattern=r"^[A-Z0-9\-]+$",
        )
    ] = None

    nombre: Optional[constr(strip_whitespace=True, min_length=2, max_length=100)] = None

    horas_presenciales: Optional[conint(ge=0)] = None
    horas_mixtas: Optional[conint(ge=0)] = None
    horas_autonomas: Optional[conint(ge=0)] = None
    cantidad_creditos: Optional[conint(ge=1, le=30)] = None
    semestre: Optional[conint(ge=1, le=12)] = None

    model_config = ConfigDict(extra="forbid")


class SeccionSecurePatch(BaseModel):
    """Schema para actualización parcial de sección"""

    codigo: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    anio_academico: Optional[conint(ge=1, le=5)] = None
    semestre: Optional[Literal[1, 2]] = None
    tipo_grupo: Optional[constr(strip_whitespace=True, to_lower=True, min_length=1, max_length=20)] = None
    numero_estudiantes: Optional[conint(ge=1, le=500)] = None
    cupos: Optional[conint(ge=1, le=500)] = None
    asignatura_id: Optional[conint(gt=0)] = None

    @field_validator("tipo_grupo")
    @classmethod
    def validate_tipo_grupo(cls, v: Optional[str]) -> Optional[str]:
        """Validar que el tipo_grupo sea válido"""
        if v is not None:
            valid_tipos = ["seccion", "mencion", "base"]
            if v not in valid_tipos:
                raise ValueError(f"tipo_grupo debe ser uno de: {', '.join(valid_tipos)}")
        return v

    model_config = ConfigDict(extra="forbid")


class SalaSecurePatch(BaseModel):
    """Schema para actualización parcial de sala"""

    codigo: Optional[
        constr(
            strip_whitespace=True,
            to_upper=True,
            min_length=1,
            max_length=100,
            pattern=r"^[A-Z0-9\-]+$",
        )
    ] = None

    capacidad: Optional[conint(ge=1, le=500)] = None
    tipo: Optional[TipoSalaEnum] = None
    disponible: Optional[bool] = None
    equipamiento: Optional[constr(max_length=500)] = None
    edificio_id: Optional[conint(gt=0)] = None

    model_config = ConfigDict(extra="forbid")


class BloqueSecurePatch(BaseModel):
    """Schema para actualización parcial de bloque"""

    dia_semana: Optional[DiaSemanaEnum] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_hours(self):
        """Valida que la hora de fin sea posterior a la hora de inicio"""
        if self.hora_fin is not None and self.hora_inicio is not None:
            if self.hora_fin <= self.hora_inicio:
                raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return self


class RestriccionSecurePatch(BaseModel):
    """Schema para actualización parcial de restricción"""

    tipo: Optional[TipoRestriccionEnum] = None
    valor: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    prioridad: Optional[conint(ge=1, le=10)] = None
    restriccion_blanda: Optional[bool] = None
    restriccion_dura: Optional[bool] = None
    activa: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")


class RestriccionHorarioSecurePatch(BaseModel):
    """Schema para actualización parcial de restricción de horario"""

    dia_semana: Optional[DiaSemanaEnum] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    disponible: Optional[bool] = None
    descripcion: Optional[constr(max_length=255)] = None
    activa: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_hours(self):
        """Valida que la hora de fin sea posterior a la hora de inicio"""
        if self.hora_fin is not None and self.hora_inicio is not None:
            if self.hora_fin <= self.hora_inicio:
                raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return self


class CampusSecurePatch(BaseModel):
    """Schema para actualización parcial de campus"""

    nombre: Optional[constr(strip_whitespace=True, min_length=2, max_length=100)] = None
    direccion: Optional[constr(max_length=200)] = None

    model_config = ConfigDict(extra="forbid")


class EdificioSecurePatch(BaseModel):
    """Schema para actualización parcial de edificio"""

    nombre: Optional[constr(strip_whitespace=True, min_length=2, max_length=100)] = None
    pisos: Optional[conint(ge=1, le=50)] = None
    campus_id: Optional[conint(gt=0)] = None

    model_config = ConfigDict(extra="forbid")


class DocenteSecurePatch(BaseModel):
    """Schema para actualización parcial de docente"""

    departamento: Optional[
        constr(strip_whitespace=True, min_length=1, max_length=100, to_upper=True)
    ] = Field(None, description="Departamento del docente")

    @field_validator("departamento")
    @classmethod
    def validate_departamento(cls, v: Optional[str]) -> Optional[str]:
        """Validar departamento"""
        if v is None:
            return v

        # Validar contra inyecciones
        BaseSecureValidator.validate_no_injection(v, "departamento")

        # Validar nombre válido
        BaseSecureValidator.validate_name(v, "departamento")

        return v

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class EstudianteSecurePatch(BaseModel):
    """
    Schema para actualización parcial de estudiante.
    La matrícula NO se puede modificar después de ser generada.
    """
    pass

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class AdministradorSecurePatch(BaseModel):
    """Schema para actualización parcial de administrador"""

    permisos: Optional[constr(strip_whitespace=True, min_length=1, max_length=500)] = Field(
        None, description="Permisos del administrador"
    )

    @field_validator("permisos")
    @classmethod
    def validate_permisos(cls, v: Optional[str]) -> Optional[str]:
        """Validar permisos"""
        if v is None:
            return v

        # Validar contra inyecciones
        BaseSecureValidator.validate_no_injection(v, "permisos")

        return v

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class ClaseSecurePatch(BaseModel):
    """Schema para actualización parcial de clase"""

    estado: Optional[EstadoClaseEnum] = None
    seccion_id: Optional[conint(gt=0)] = None
    docente_id: Optional[conint(gt=0)] = Field(None, description="ID del docente (user_id del docente)")
    sala_id: Optional[conint(gt=0)] = None
    bloque_id: Optional[conint(gt=0)] = None

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# SCHEMAS DE CONSULTA - Para filtros en endpoints
# ============================================================================


class PaginationParams(BaseModel):
    """Parámetros de paginación seguros"""

    skip: conint(ge=0, le=10000) = Field(default=0, description="Número de registros a saltar")

    limit: conint(ge=1, le=100) = Field(
        default=20, description="Número máximo de registros a retornar"
    )


class SearchParams(BaseModel, BaseSecureValidator):
    """Parámetros de búsqueda seguros"""

    query: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = Field(
        None, description="Término de búsqueda"
    )

    @field_validator("query")
    @classmethod
    def validate_search_query(cls, v: Optional[str]) -> Optional[str]:
        """Validación de término de búsqueda"""
        if v is None:
            return None

        # Validar contra inyección
        cls.validate_no_injection(v, "término de búsqueda")

        # Sanitizar caracteres especiales de SQL
        dangerous_chars = ["%", "_", "[", "]", "^"]
        for char in dangerous_chars:
            if char in v:
                raise ValueError(
                    f"El término de búsqueda contiene caracteres no permitidos: {char}"
                )

        return v


# ============================================================================
# CONFIGURACIÓN DE MODELO BASE
# ============================================================================

# ============================================================================
# SCHEMAS DE RECUPERACIÓN DE CONTRASEÑA - Con validaciones de seguridad
# ============================================================================


class PasswordChangeSchema(BaseModel, BaseSecureValidator):
    """
    Schema para cambio de contraseña de usuario autenticado.
    
    Requiere:
    - Contraseña actual (para verificación)
    - Nueva contraseña segura
    """
    contrasena_actual: constr(min_length=8, max_length=128) = Field(
        ...,
        description="Contraseña actual del usuario"
    )

    contrasena_nueva: constr(min_length=12, max_length=128) = Field(
        ...,
        description="Nueva contraseña segura"
    )

    @field_validator("contrasena_actual")
    @classmethod
    def validate_current_password(cls, v: str) -> str:
        """Validación básica de contraseña actual"""
        # Prevenir caracteres de control
        if re.search(r"[\x00-\x1F\x7F]", v):
            raise ValueError("Contraseña inválida")
        return v

    @field_validator("contrasena_nueva")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        """
        Validación exhaustiva de fortaleza de contraseña.
        Mismos requisitos que al crear usuario.
        """
        # Longitud mínima
        if len(v) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres")

        # Longitud máxima (prevenir DoS)
        if len(v) > 128:
            raise ValueError("La contraseña es demasiado larga (máximo 128 caracteres)")

        # Al menos una mayúscula
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")

        # Al menos una minúscula
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")

        # Al menos un número
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")

        # Al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/~`]', v):
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial "
                '(!@#$%^&*(),.?":{}|<>_-+=[]\\;/~`)'
            )

        # Prevenir contraseñas con caracteres de control
        if re.search(r"[\x00-\x1F\x7F]", v):
            raise ValueError("La contraseña contiene caracteres no permitidos")

        # Prevenir caracteres repetidos excesivos
        if len(set(v)) < 6:
            raise ValueError("La contraseña debe tener mayor variedad de caracteres")

        return v

    @model_validator(mode="after")
    def validate_passwords_different(self):
        """Validar que la nueva contraseña sea diferente de la actual"""
        if self.contrasena_actual == self.contrasena_nueva:
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        return self

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class PasswordChangeSuccessSchema(BaseModel):
    """Schema de respuesta para cambio exitoso de contraseña"""
    mensaje: str = Field(
        ...,
        description="Mensaje de confirmación"
    )
    
    email: str = Field(
        ...,
        description="Email del usuario"
    )

    model_config = ConfigDict(extra="forbid")


class PasswordResetRequestSchema(BaseModel, BaseSecureValidator):
    """
    Schema para solicitar recuperación de contraseña.
    
    Solo requiere el email del usuario.
    """
    email: EmailStr = Field(
        ...,
        description="Email del usuario que solicita recuperar su contraseña",
        examples=["usuario@ejemplo.cl"]
    )

    @field_validator("email")
    @classmethod
    def validate_email_secure(cls, v: str) -> str:
        """Validación adicional del email contra inyección"""
        # EmailStr ya valida formato, pero agregamos validación anti-inyección
        cls.validate_no_injection(v, "email")

        # Validar longitud máxima del email
        if len(v) > 254:  # RFC 5321
            raise ValueError("El email es demasiado largo (máximo 254 caracteres)")

        # Validar dominio (parte después del @)
        domain = v.split("@")[1]
        if len(domain) > 253:
            raise ValueError("El dominio del email es demasiado largo")

        return v.lower()

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class PasswordResetConfirmSchema(BaseModel, BaseSecureValidator):
    """
    Schema para confirmar recuperación de contraseña con nueva contraseña.
    
    Requiere:
    - Token de recuperación
    - Nueva contraseña segura
    """
    token: constr(strip_whitespace=True, min_length=32, max_length=256) = Field(
        ...,
        description="Token de recuperación recibido por email"
    )

    nueva_contrasena: constr(min_length=12, max_length=128) = Field(
        ...,
        description="Nueva contraseña segura"
    )

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validar formato del token"""
        # Validar contra inyección
        cls.validate_no_injection(v, "token")
        
        # El token debe ser alfanumérico (base64url)
        if not re.match(r"^[A-Za-z0-9_-]+$", v):
            raise ValueError("Token inválido")
        
        return v

    @field_validator("nueva_contrasena")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validación exhaustiva de fortaleza de contraseña.
        Mismos requisitos que al crear usuario.
        """
        # Longitud mínima
        if len(v) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres")

        # Longitud máxima (prevenir DoS)
        if len(v) > 128:
            raise ValueError("La contraseña es demasiado larga (máximo 128 caracteres)")

        # Al menos una mayúscula
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")

        # Al menos una minúscula
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")

        # Al menos un número
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")

        # Al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/~`]', v):
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial "
                '(!@#$%^&*(),.?":{}|<>_-+=[]\\;/~`)'
            )

        # Prevenir contraseñas con caracteres de control
        if re.search(r"[\x00-\x1F\x7F]", v):
            raise ValueError("La contraseña contiene caracteres no permitidos")

        # Prevenir caracteres repetidos excesivos
        if len(set(v)) < 6:
            raise ValueError("La contraseña debe tener mayor variedad de caracteres")

        return v

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class PasswordResetResponseSchema(BaseModel):
    """
    Schema de respuesta para solicitud de recuperación.
    
    IMPORTANTE: Siempre retorna el mismo mensaje exitoso,
    independientemente de si el email existe o no.
    Esto previene enumeración de usuarios.
    """
    mensaje: str = Field(
        ...,
        description="Mensaje de confirmación"
    )
    
    email: str = Field(
        ...,
        description="Email al que se envió el link (o donde se enviaría)"
    )

    model_config = ConfigDict(extra="forbid")


class PasswordResetSuccessSchema(BaseModel):
    """
    Schema de respuesta para recuperación exitosa.
    """
    mensaje: str = Field(
        ...,
        description="Mensaje de confirmación"
    )
    
    email: Optional[str] = Field(
        None,
        description="Email del usuario (opcional)"
    )

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# CONFIGURACIÓN DE MODELO BASE
# ============================================================================

# Configurar todos los modelos para que no permitan campos extras
for schema_class in [
    UserSecureBase,
    UserSecureCreate,
    UserSecureLogin,
    AsignaturaSecureBase,
    AsignaturaSecureCreate,
    SeccionSecureBase,
    SeccionSecureCreate,
    SalaSecureBase,
    SalaSecureCreate,
    BloqueSecureBase,
    BloqueSecureCreate,
    RestriccionSecureBase,
    RestriccionSecureCreate,
    RestriccionHorarioSecureBase,
    RestriccionHorarioSecureCreate,
    CampusSecureBase,
    CampusSecureCreate,
    EdificioSecureBase,
    EdificioSecureCreate,
    ClaseSecureBase,
    ClaseSecureCreate,
    DocenteSecureBase,
    DocenteSecureCreate,
    EstudianteSecureBase,
    EstudianteSecureCreate,
    AdministradorSecureBase,
    AdministradorSecureCreate,
]:
    if not hasattr(schema_class, "model_config"):
        schema_class.model_config = ConfigDict(extra="forbid")
