from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import relationship

from infrastructure.database.config import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    pass_hash = Column(Text, nullable=False)
    rol = Column(String(20), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp())
    deleted_at = Column(DateTime, nullable=True, default=None)  # Soft delete timestamp

    # Relaciones inversas
    docente = relationship("Docente", back_populates="user", uselist=False)
    estudiante = relationship("Estudiante", back_populates="user", uselist=False)
    administrador = relationship("Administrador", back_populates="user", uselist=False)


class Docente(Base):
    __tablename__ = "docente"

    # user_id es ahora la clave primaria (sin id separado)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, nullable=False)
    departamento = Column(Text)

    user = relationship("User", back_populates="docente")
    clases = relationship("Clase", back_populates="docente")
    restricciones = relationship("Restriccion", back_populates="docente")
    restricciones_horario = relationship("RestriccionHorario", back_populates="docente")


class Estudiante(Base):
    __tablename__ = "estudiante"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    matricula = Column(Text, nullable=False, unique=True)  # Generada automáticamente

    user = relationship("User", back_populates="estudiante")
    inscripciones = relationship(
        "EstudianteSeccion",
        back_populates="estudiante",
        cascade="all, delete-orphan",
    )
    secciones = relationship(
        "Seccion",
        secondary="estudiante_seccion",
        back_populates="estudiantes",
        viewonly=True,
    )


class Administrador(Base):
    __tablename__ = "administrador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    permisos = Column(Text)

    user = relationship("User", back_populates="administrador")


class Campus(Base):
    __tablename__ = "campus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    direccion = Column(Text)

    edificios = relationship("Edificio", back_populates="campus")


class Edificio(Base):
    __tablename__ = "edificio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campus_id = Column(Integer, ForeignKey("campus.id"))
    nombre = Column(Text, nullable=False)
    pisos = Column(Integer)

    campus = relationship("Campus", back_populates="edificios")
    salas = relationship("Sala", back_populates="edificio")


class RestriccionHorario(Base):
    __tablename__ = "restriccion_horario"

    id = Column(Integer, primary_key=True, autoincrement=True)
    docente_id = Column(Integer, ForeignKey("docente.user_id"), nullable=False)
    dia_semana = Column(Integer)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)
    disponible = Column(Boolean, default=True)
    descripcion = Column(Text, nullable=True)
    activa = Column(Boolean, default=True)

    docente = relationship("Docente", back_populates="restricciones_horario", foreign_keys=[docente_id])


class Asignatura(Base):
    __tablename__ = "asignatura"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(Text, nullable=False)
    nombre = Column(Text, nullable=False)
    horas_presenciales = Column(Integer, nullable=False)
    horas_mixtas = Column(Integer, nullable=False)
    horas_autonomas = Column(Integer, nullable=False)
    cantidad_creditos = Column(Integer, nullable=False)
    semestre = Column(Integer, nullable=False)

    secciones = relationship("Seccion", back_populates="asignatura")


class Seccion(Base):
    __tablename__ = "seccion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(Text, nullable=False)  # Ej: "1 sección 1", "5 mención 1"
    anio_academico = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5
    semestre = Column(Integer)  # Semestre académico (1, 2)
    asignatura_id = Column(Integer, ForeignKey("asignatura.id"))
    tipo_grupo = Column(String(20), nullable=False, default="seccion")  # "seccion", "mencion", "base"
    numero_estudiantes = Column(Integer, nullable=False, default=30)  # Cantidad de estudiantes en el grupo
    cupos = Column(Integer)  # Cupos disponibles (puede ser diferente de numero_estudiantes)

    asignatura = relationship("Asignatura", back_populates="secciones")
    clases = relationship("Clase", back_populates="seccion")
    inscripciones = relationship(
        "EstudianteSeccion",
        back_populates="seccion",
        cascade="all, delete-orphan",
    )
    estudiantes = relationship(
        "Estudiante",
        secondary="estudiante_seccion",
        back_populates="secciones",
        viewonly=True,
    )


class EstudianteSeccion(Base):
    __tablename__ = "estudiante_seccion"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "seccion_id", name="uq_estudiante_seccion"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    estudiante_id = Column(Integer, ForeignKey("estudiante.id", ondelete="CASCADE"), nullable=False)
    seccion_id = Column(Integer, ForeignKey("seccion.id", ondelete="CASCADE"), nullable=False)
    fecha_inscripcion = Column(DateTime, default=func.current_timestamp(), nullable=False)

    estudiante = relationship("Estudiante", back_populates="inscripciones")
    seccion = relationship("Seccion", back_populates="inscripciones")


class Sala(Base):
    __tablename__ = "sala"

    id = Column(Integer, primary_key=True, autoincrement=True)
    edificio_id = Column(Integer, ForeignKey("edificio.id"))
    codigo = Column(Text, nullable=False)
    capacidad = Column(Integer)
    tipo = Column(Text)
    disponible = Column(Boolean, default=True)
    equipamiento = Column(Text)

    edificio = relationship("Edificio", back_populates="salas")
    clases = relationship("Clase", back_populates="sala")


class Bloque(Base):
    __tablename__ = "bloque"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dia_semana = Column(Integer)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)

    clases = relationship("Clase", back_populates="bloque")


class Clase(Base):
    __tablename__ = "clase"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seccion_id = Column(Integer, ForeignKey("seccion.id"))
    docente_id = Column(Integer, ForeignKey("docente.user_id"), nullable=False)
    sala_id = Column(Integer, ForeignKey("sala.id"))
    bloque_id = Column(Integer, ForeignKey("bloque.id"))
    estado = Column(Text)

    seccion = relationship("Seccion", back_populates="clases")
    docente = relationship("Docente", back_populates="clases", foreign_keys=[docente_id])
    sala = relationship("Sala", back_populates="clases")
    bloque = relationship("Bloque", back_populates="clases")
    eventos = relationship("Evento", back_populates="clase")


class Restriccion(Base):
    __tablename__ = "restriccion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    docente_id = Column(Integer, ForeignKey("docente.user_id"), nullable=False)
    tipo = Column(Text)
    valor = Column(Text)
    prioridad = Column(Integer)
    restriccion_blanda = Column(Boolean, default=False)
    restriccion_dura = Column(Boolean, default=False)
    activa = Column(Boolean, default=True)

    docente = relationship("Docente", back_populates="restricciones", foreign_keys=[docente_id])


class Evento(Base):
    """
    Modelo para eventos del docente.
    
    Los eventos pueden ser:
    - Asociados a una clase específica (clase_id presente): incluye asignatura, día, horario, visible para estudiantes
    - Eventos personales/departamento (clase_id NULL): reuniones, eventos administrativos, etc.
    
    Navegación cuando clase_id presente: Evento → Clase → Seccion → Asignatura/Bloque/Estudiantes
    """
    __tablename__ = "evento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    docente_id = Column(Integer, ForeignKey("docente.user_id"), nullable=False)
    clase_id = Column(Integer, ForeignKey("clase.id"), nullable=True)  # Opcional: permite eventos sin clase específica
    nombre = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(Date, nullable=False)  # Fecha del evento
    hora_inicio = Column(Time, nullable=False)
    hora_cierre = Column(Time, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    docente = relationship("Docente", backref="eventos", foreign_keys=[docente_id])
    clase = relationship("Clase", back_populates="eventos")


class PasswordResetToken(Base):
    """
    Modelo para tokens de recuperación de contraseña.
    
    Características de seguridad:
    - Token hash almacenado (nunca el token en texto plano)
    - Expiración automática después de 1 hora
    - Un solo uso por token
    - Registro de uso para auditoría
    """
    __tablename__ = "password_reset_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Token hasheado (nunca almacenar el token real)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Control de expiración
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    
    # Control de uso
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # IP del solicitante (para auditoría)
    request_ip = Column(String(45), nullable=True)  # IPv6 max length
    
    # Relación con usuario
    user = relationship("User", backref="password_reset_tokens")


class PasswordResetAttempt(Base):
    """
    Modelo para registrar intentos de recuperación de contraseña.
    
    Usado para:
    - Auditoría de seguridad
    - Detección de ataques de fuerza bruta
    - Rate limiting por email/IP
    """
    __tablename__ = "password_reset_attempt"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Email solicitado (puede no existir en el sistema)
    email = Column(String(254), nullable=False, index=True)
    
    # IP del solicitante
    ip_address = Column(String(45), nullable=False, index=True)
    
    # Timestamps
    attempted_at = Column(DateTime, default=func.current_timestamp(), nullable=False, index=True)
    
    # Resultado del intento
    success = Column(Boolean, default=False, nullable=False)
    
    # Razón de fallo (si aplica)
    failure_reason = Column(String(100), nullable=True)
    
    # User agent para detección de bots
    user_agent = Column(Text, nullable=True)
