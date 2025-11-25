"""Add fecha to evento table

Revision ID: b5c6d7e8f9g0
Revises: a3b4c5d6e7f8
Create Date: 2025-11-18 19:50:00.000000

Esta migración agrega el campo fecha a la tabla evento para permitir
especificar la fecha exacta en que ocurrirá el evento.

Cambios:
- Agrega columna 'fecha' (Date, NOT NULL) a la tabla evento
- Establece fecha por defecto como CURRENT_DATE para eventos existentes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c6d7e8f9g0'
down_revision: Union[str, None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Agrega fecha a la tabla evento.
    """
    print("\n" + "="*80)
    print("🔄 INICIANDO MIGRACIÓN: Agregar fecha a evento")
    print("="*80)
    print()

    # Paso 1: Agregar columna fecha con valor por defecto temporal
    print("📋 PASO 1: Agregando columna fecha...")
    print("  → Agregando con valor por defecto CURRENT_DATE para registros existentes")
    op.add_column('evento', 
        sa.Column('fecha', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE'))
    )
    print("  ✓ Columna fecha agregada (Date, NOT NULL)")
    print()

    # Paso 2: Remover el valor por defecto (solo necesario para registros existentes)
    print("📋 PASO 2: Removiendo valor por defecto...")
    op.alter_column('evento', 'fecha', server_default=None)
    print("  ✓ Valor por defecto removido (nuevos registros deben especificar fecha)")
    print()

    print("="*80)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80)
    print()
    print("Cambios aplicados:")
    print("  ✓ evento.fecha agregado (Date, NOT NULL)")
    print()
    print("Eventos existentes:")
    print("  → Fecha establecida a la fecha actual (CURRENT_DATE)")
    print()
    print("Nuevos eventos:")
    print("  → Deben especificar la fecha obligatoriamente")
    print()


def downgrade() -> None:
    """
    Revierte los cambios: elimina fecha de evento.
    """
    print("\n" + "="*80)
    print("⏮️  REVERTIENDO MIGRACIÓN: Eliminar fecha de evento")
    print("="*80)
    print()

    print("📋 Eliminando columna fecha...")
    op.drop_column('evento', 'fecha')
    print("  ✓ Columna eliminada")
    print()

    print("="*80)
    print("✅ ROLLBACK COMPLETADO")
    print("="*80)
    print()
