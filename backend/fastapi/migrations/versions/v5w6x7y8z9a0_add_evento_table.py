"""add_evento_table

Revision ID: v5w6x7y8z9a0
Revises: p4q5r6s7t8u9
Create Date: 2025-11-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'v5w6x7y8z9a0'
down_revision: Union[str, Sequence[str], None] = 'p4q5r6s7t8u9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Crear tabla de eventos para que los docentes puedan gestionar sus eventos.
    
    Características:
    - Los docentes pueden crear, editar y eliminar sus propios eventos
    - Los estudiantes pueden consultar eventos
    - Los administradores pueden supervisar y habilitar/deshabilitar eventos
    """
    op.create_table(
        'evento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('docente_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('hora_inicio', sa.Time(), nullable=False),
        sa.Column('hora_cierre', sa.Time(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['docente_id'], ['docente.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para mejorar el rendimiento de consultas
    op.create_index('ix_evento_docente_id', 'evento', ['docente_id'])
    op.create_index('ix_evento_activo', 'evento', ['activo'])
    op.create_index('ix_evento_created_at', 'evento', ['created_at'])


def downgrade() -> None:
    """Revertir la creación de la tabla evento"""
    op.drop_index('ix_evento_created_at', table_name='evento')
    op.drop_index('ix_evento_activo', table_name='evento')
    op.drop_index('ix_evento_docente_id', table_name='evento')
    op.drop_table('evento')
