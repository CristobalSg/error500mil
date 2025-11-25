"""Add estudiante_seccion association table

Revision ID: c7d8e9f0a1b2
Revises: b5c6d7e8f9g0
Create Date: 2025-12-05 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = 'b5c6d7e8f9g0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create join table between estudiantes and secciones."""
    op.create_table(
        'estudiante_seccion',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            'estudiante_id',
            sa.Integer(),
            sa.ForeignKey('estudiante.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'seccion_id',
            sa.Integer(),
            sa.ForeignKey('seccion.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'fecha_inscripcion',
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint('estudiante_id', 'seccion_id', name='uq_estudiante_seccion'),
    )


def downgrade() -> None:
    """Drop join table between estudiantes and secciones."""
    op.drop_table('estudiante_seccion')
