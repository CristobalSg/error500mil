"""
Schemas para la generación de horarios con FET
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ============================================================================
# METADATA
# ============================================================================


class TimetableMetadata(BaseModel):
    """Metadata del horario a generar"""

    timetable_id: str = Field(..., description="ID único del horario")
    semester: str = Field(..., description="Semestre (ej: 2025-1)")
    institution_name: str = Field(..., description="Nombre de la institución")
    comments: str = Field(default="", description="Comentarios adicionales")


# ============================================================================
# CALENDAR
# ============================================================================


class CalendarDay(BaseModel):
    """Día de la semana"""

    index: int = Field(..., ge=0, le=6, description="Índice del día (0-6)")
    name: str = Field(..., description="Nombre corto del día")
    long_name: str = Field(..., description="Nombre largo del día")


class CalendarHour(BaseModel):
    """Hora/bloque del calendario"""

    index: int = Field(..., ge=0, description="Índice de la hora")
    name: str = Field(..., description="Rango horario (ej: 08:00 - 09:00)")
    long_name: str = Field(..., description="Nombre del bloque (ej: Bloque 1)")


class Calendar(BaseModel):
    """Calendario con días y bloques horarios"""

    days: List[CalendarDay] = Field(..., description="Días de la semana")
    hours: List[CalendarHour] = Field(..., description="Bloques horarios")


# ============================================================================
# SUBJECTS
# ============================================================================


class Subject(BaseModel):
    """Asignatura/materia"""

    id: str = Field(..., description="ID único de la asignatura")
    name: str = Field(..., description="Nombre de la asignatura")
    code: str = Field(..., description="Código de la asignatura")
    comments: str = Field(default="", description="Comentarios")


# ============================================================================
# TEACHERS
# ============================================================================


class Teacher(BaseModel):
    """Docente"""

    id: str = Field(..., description="ID único del docente")
    name: str = Field(..., description="Nombre completo del docente")
    target_hours: int = Field(default=0, ge=0, description="Horas objetivo")
    comments: str = Field(default="", description="Comentarios")


# ============================================================================
# STUDENT YEARS & GROUPS
# ============================================================================


class StudentGroup(BaseModel):
    """Grupo de estudiantes (sección)"""

    id: str = Field(..., description="ID único del grupo")
    name: str = Field(..., description="Nombre del grupo (ej: '1 sección 1')")
    students: int = Field(..., ge=1, description="Cantidad de estudiantes")


class StudentYear(BaseModel):
    """Año académico con sus grupos"""

    id: str = Field(..., description="ID único del año")
    name: str = Field(..., description="Nombre del año (ej: '1', '2')")
    total_students: int = Field(..., ge=0, description="Total de estudiantes")
    groups: List[StudentGroup] = Field(..., description="Grupos/secciones del año")


# ============================================================================
# ACTIVITIES
# ============================================================================


class StudentsReference(BaseModel):
    """Referencia a estudiantes (por año o grupo)"""

    type: Literal["year", "group"] = Field(..., description="Tipo de referencia")
    id: str = Field(..., description="ID del año o grupo")


class Activity(BaseModel):
    """Actividad académica (clase)"""

    id: str = Field(..., description="ID único de la actividad")
    group_id: str = Field(..., description="ID del grupo de actividades en FET")
    teacher_id: str = Field(..., description="ID del docente")
    subject_id: str = Field(..., description="ID de la asignatura")
    students_reference: StudentsReference = Field(..., description="Referencia a estudiantes")
    duration: int = Field(..., ge=1, description="Duración en bloques consecutivos")
    total_duration: int = Field(..., ge=1, description="Duración total semanal")
    active: bool = Field(default=True, description="Si la actividad está activa")
    comments: str = Field(default="", description="Comentarios")


# ============================================================================
# TIME CONSTRAINTS
# ============================================================================


class NotAvailableSlot(BaseModel):
    """Slot de tiempo no disponible"""

    day_index: int = Field(..., ge=0, description="Índice del día")
    hour_index: int = Field(..., ge=0, description="Índice de la hora")


class TimeConstraintBase(BaseModel):
    """Base para restricciones de tiempo"""

    type: str = Field(..., description="Tipo de restricción")
    weight: float = Field(..., ge=0, le=100, description="Peso/prioridad (0-100)")
    active: bool = Field(default=True, description="Si la restricción está activa")


class BasicCompulsoryTimeConstraint(TimeConstraintBase):
    """Restricción básica obligatoria de tiempo"""

    type: Literal["basic_compulsory_time"] = "basic_compulsory_time"


class MinDaysBetweenActivitiesConstraint(TimeConstraintBase):
    """Mínimo de días entre actividades"""

    type: Literal["min_days_between_activities"] = "min_days_between_activities"
    min_days: int = Field(..., ge=1, description="Días mínimos entre actividades")
    activity_ids: List[str] = Field(..., description="IDs de actividades")


class TeacherNotAvailableConstraint(TimeConstraintBase):
    """Docente no disponible en ciertos horarios"""

    type: Literal["teacher_not_available"] = "teacher_not_available"
    teacher_id: str = Field(..., description="ID del docente")
    not_available_slots: List[NotAvailableSlot] = Field(
        ..., description="Slots no disponibles"
    )


# Union de todas las restricciones de tiempo
TimeConstraint = (
    BasicCompulsoryTimeConstraint
    | MinDaysBetweenActivitiesConstraint
    | TeacherNotAvailableConstraint
)


# ============================================================================
# SPACE (BUILDINGS & ROOMS)
# ============================================================================


class Building(BaseModel):
    """Edificio"""

    id: str = Field(..., description="ID único del edificio")
    name: str = Field(..., description="Nombre del edificio")
    comments: str = Field(default="", description="Comentarios")


class Room(BaseModel):
    """Sala/aula"""

    id: str = Field(..., description="ID único de la sala")
    name: str = Field(..., description="Nombre de la sala")
    building_id: str = Field(..., description="ID del edificio")
    capacity: int = Field(..., ge=1, description="Capacidad de estudiantes")
    comments: str = Field(default="", description="Comentarios")


class SpaceConstraintBase(BaseModel):
    """Base para restricciones de espacio"""

    type: str = Field(..., description="Tipo de restricción")
    weight: float = Field(..., ge=0, le=100, description="Peso/prioridad (0-100)")
    active: bool = Field(default=True, description="Si la restricción está activa")


class BasicCompulsorySpaceConstraint(SpaceConstraintBase):
    """Restricción básica obligatoria de espacio"""

    type: Literal["basic_compulsory_space"] = "basic_compulsory_space"


# Union de todas las restricciones de espacio
SpaceConstraint = BasicCompulsorySpaceConstraint


class Space(BaseModel):
    """Configuración de espacios físicos"""

    buildings: List[Building] = Field(default=[], description="Lista de edificios")
    rooms: List[Room] = Field(default=[], description="Lista de salas")
    space_constraints: List[SpaceConstraint] = Field(
        default=[], description="Restricciones de espacio"
    )


# ============================================================================
# MAIN REQUEST
# ============================================================================


class TimetableGenerationRequest(BaseModel):
    """Request completo para generación de horarios"""

    metadata: TimetableMetadata = Field(..., description="Metadata del horario")
    calendar: Calendar = Field(..., description="Calendario con días y horas")
    subjects: List[Subject] = Field(..., description="Lista de asignaturas")
    teachers: List[Teacher] = Field(..., description="Lista de docentes")
    student_years: List[StudentYear] = Field(..., description="Años y grupos de estudiantes")
    activities: List[Activity] = Field(..., description="Actividades académicas")
    time_constraints: List[TimeConstraint] = Field(
        ..., description="Restricciones de tiempo"
    )
    space: Space = Field(..., description="Configuración de espacios")


# ============================================================================
# RESPONSE
# ============================================================================


class TimetableGenerationResponse(BaseModel):
    """Respuesta de la generación de horarios"""

    success: bool = Field(..., description="Si la generación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    timetable_id: str = Field(..., description="ID del horario generado")
    file_url: Optional[str] = Field(None, description="URL del archivo FET generado")
    errors: List[str] = Field(default=[], description="Lista de errores si los hay")
