"""update_seccion_estructura_nueva

Revision ID: 3dc2453812ae
Revises: c7d8e9f0a1b2
Create Date: 2025-11-19 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3dc2453812ae'
down_revision: Union[str, Sequence[str], None] = 'c7d8e9f0a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Actualizar estructura de seccion."""
    
    # 1. Agregar nuevas columnas a seccion permitiendo NULL temporalmente
    op.add_column('seccion', sa.Column('anio_academico', sa.Integer(), nullable=True))
    op.add_column('seccion', sa.Column('tipo_grupo', sa.String(length=20), nullable=True))
    op.add_column('seccion', sa.Column('numero_estudiantes', sa.Integer(), nullable=True))
    
    # 2. Migrar datos existentes
    # Si existe la columna anio, copiar sus valores a anio_academico
    op.execute("""
        UPDATE seccion 
        SET anio_academico = CASE 
            WHEN anio >= 2020 AND anio <= 2030 THEN 1
            ELSE 1
        END
        WHERE anio_academico IS NULL
    """)
    
    # Establecer valores por defecto
    op.execute("UPDATE seccion SET tipo_grupo = 'seccion' WHERE tipo_grupo IS NULL")
    op.execute("UPDATE seccion SET numero_estudiantes = COALESCE(cupos, 30) WHERE numero_estudiantes IS NULL")
    
    # 3. Hacer las columnas NOT NULL
    op.alter_column('seccion', 'anio_academico', nullable=False)
    op.alter_column('seccion', 'tipo_grupo', nullable=False)
    op.alter_column('seccion', 'numero_estudiantes', nullable=False)
    
    # 4. Eliminar columna anio antigua si existe
    op.execute("ALTER TABLE seccion DROP COLUMN IF EXISTS anio")


def downgrade() -> None:
    """Downgrade schema - Revertir cambios en seccion."""
    
    # 1. Recrear columna anio
    op.add_column('seccion', sa.Column('anio', sa.INTEGER(), autoincrement=False, nullable=True))
    
    # 2. Migrar datos de vuelta (poner un año por defecto basado en anio_academico)
    op.execute("UPDATE seccion SET anio = 2024 WHERE anio IS NULL")
    
    # 3. Eliminar nuevas columnas
    op.drop_column('seccion', 'numero_estudiantes')
    op.drop_column('seccion', 'tipo_grupo')
    op.drop_column('seccion', 'anio_academico')
