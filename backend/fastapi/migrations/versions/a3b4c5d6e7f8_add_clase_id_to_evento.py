"""Add clase_id to evento table

Revision ID: a3b4c5d6e7f8
Revises: z1a2b3c4d5e6
Create Date: 2025-11-18 03:45:00.000000

Esta migración agrega la capacidad de asociar eventos a clases específicas:
1. Agrega columna 'clase_id' (nullable) a la tabla evento
2. Crea foreign key clase_id → clase.id

Casos de uso:
- Si clase_id es NULL: evento personal del docente
- Si clase_id está presente: evento asociado a una clase
  * Incluye automáticamente: asignatura, día, horario (via clase.bloque)
  * Visible para estudiantes de esa sección
  * Navegación: Evento → Clase → Seccion → Asignatura/Bloque

Ejemplo de flujo:
  Docente: "Quiero crear evento el viernes en Arquitectura de Software"
  → Sistema busca clase del docente donde:
     - clase.seccion.asignatura = "Arquitectura de Software"
     - clase.bloque.dia_semana = 5 (viernes)
  → Crea evento con ese clase_id
  → Estudiantes de esa sección pueden ver el evento
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, None] = 'z1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Agrega clase_id a la tabla evento para vincular eventos con clases específicas.
    """
    print("\n" + "="*80)
    print("🔄 INICIANDO MIGRACIÓN: Agregar clase_id a evento")
    print("="*80)
    print()

    # Paso 1: Agregar columna clase_id (nullable para permitir eventos personales)
    print("📋 PASO 1: Agregando columna clase_id...")
    op.add_column('evento', 
        sa.Column('clase_id', sa.Integer(), nullable=True)
    )
    print("  ✓ Columna clase_id agregada (nullable=True)")
    print()

    # Paso 2: Crear foreign key constraint
    print("🔗 PASO 2: Creando foreign key constraint...")
    op.create_foreign_key(
        'evento_clase_id_fkey',  # Nombre del constraint
        'evento',                 # Tabla origen
        'clase',                  # Tabla destino
        ['clase_id'],            # Columna origen
        ['id']                   # Columna destino
    )
    print("  ✓ FK evento.clase_id → clase.id creada")
    print()

    # Paso 3: Crear índice para mejorar performance en consultas
    print("📊 PASO 3: Creando índice para clase_id...")
    op.create_index(
        'ix_evento_clase_id',
        'evento',
        ['clase_id'],
        unique=False
    )
    print("  ✓ Índice ix_evento_clase_id creado")
    print()

    print("="*80)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80)
    print()
    print("Cambios aplicados:")
    print("  ✓ evento.clase_id agregado (Integer, nullable)")
    print("  ✓ FK evento.clase_id → clase.id creada")
    print("  ✓ Índice ix_evento_clase_id creado")
    print()
    print("Eventos existentes:")
    print("  → Mantienen clase_id = NULL (eventos personales)")
    print()
    print("Nuevos eventos pueden:")
    print("  → Ser personales (clase_id = NULL)")
    print("  → Estar asociados a una clase (clase_id = ID)")
    print()


def downgrade() -> None:
    """
    Revierte los cambios: elimina clase_id de evento.
    """
    print("\n" + "="*80)
    print("⏮️  REVERTIENDO MIGRACIÓN: Eliminar clase_id de evento")
    print("="*80)
    print()

    # Paso 1: Eliminar índice
    print("📊 Eliminando índice...")
    op.drop_index('ix_evento_clase_id', table_name='evento')
    print("  ✓ Índice eliminado")
    print()

    # Paso 2: Eliminar foreign key
    print("🔗 Eliminando foreign key constraint...")
    op.drop_constraint('evento_clase_id_fkey', 'evento', type_='foreignkey')
    print("  ✓ FK eliminada")
    print()

    # Paso 3: Eliminar columna
    print("📋 Eliminando columna clase_id...")
    op.drop_column('evento', 'clase_id')
    print("  ✓ Columna eliminada")
    print()

    print("="*80)
    print("✅ ROLLBACK COMPLETADO")
    print("="*80)
    print()
