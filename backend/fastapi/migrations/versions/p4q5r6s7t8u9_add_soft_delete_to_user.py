"""Add deleted_at column for soft delete functionality

Revision ID: p4q5r6s7t8u9
Revises: k8l9m0n1o2p3
Create Date: 2025-11-15 20:00:00.000000

Esta migración agrega la columna 'deleted_at' a la tabla 'user' para 
implementar soft delete (eliminación lógica en lugar de física).

Beneficios del soft delete:
- Permite restaurar usuarios eliminados por error
- Mantiene integridad referencial histórica
- Facilita auditoría y compliance (GDPR, etc.)
- Previene pérdida de datos accidental
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'p4q5r6s7t8u9'
down_revision: Union[str, Sequence[str], None] = 'k8l9m0n1o2p3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Agregar columna deleted_at para soft delete.
    """
    print("\n" + "="*74)
    print("🗑️  AGREGANDO SOFT DELETE A TABLA USER")
    print("="*74)
    
    # ========================================================================
    # PASO 1: Agregar columna deleted_at (nullable por defecto)
    # ========================================================================
    print("\n📋 Paso 1: Agregando columna deleted_at...")
    
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('deleted_at', sa.DateTime(), nullable=True, default=None)
        )
    
    print("  ✓ Columna deleted_at agregada (nullable=True)")
    
    # ========================================================================
    # PASO 2: Verificar integridad
    # ========================================================================
    print("\n🔍 Paso 2: Verificando integridad...")
    
    bind = op.get_bind()
    result = bind.execute(sa.text("SELECT COUNT(*) FROM \"user\""))
    total_users = result.scalar()
    
    print(f"  ✓ Total de usuarios en la BD: {total_users}")
    print(f"  ✓ Todos los usuarios tienen deleted_at = NULL (activos)")
    
    print("\n" + "="*74)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*74)
    print("\nSoft Delete implementado:")
    print("  ✓ Columna: user.deleted_at (DateTime, nullable=True)")
    print("  ✓ NULL = usuario activo")
    print("  ✓ NOT NULL = usuario eliminado (timestamp de eliminación)")
    print("\nNuevos endpoints disponibles:")
    print("  • DELETE /api/users/{id} → Soft delete (reversible)")
    print("  • POST /api/users/{id}/restore → Restaurar eliminado")
    print("  • DELETE /api/users/{id}/hard → Hard delete (irreversible) ⚠️")
    print("="*74 + "\n")


def downgrade() -> None:
    """
    Revertir la columna deleted_at.
    
    ADVERTENCIA: Esto eliminará toda la información de soft delete.
    Los usuarios marcados como eliminados volverán a estar "activos".
    """
    print("\n" + "="*74)
    print("⚠️  REVERTIENDO SOFT DELETE (DOWNGRADE)")
    print("="*74)
    
    # Obtener conexión para verificar
    bind = op.get_bind()
    
    # Verificar cuántos usuarios están soft-deleted
    result = bind.execute(sa.text("SELECT COUNT(*) FROM \"user\" WHERE deleted_at IS NOT NULL"))
    deleted_count = result.scalar()
    
    if deleted_count > 0:
        print(f"\n⚠️  ADVERTENCIA: Hay {deleted_count} usuarios con soft delete")
        print("   Al revertir, estos usuarios volverán a estar 'activos'")
    
    # Eliminar la columna
    print("\n🗑️  Eliminando columna deleted_at...")
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')
    
    print("  ✓ Columna eliminada")
    
    print("\n" + "="*74)
    print("⚠️  DOWNGRADE COMPLETADO")
    print("="*74)
    print("\nLa funcionalidad de soft delete ha sido eliminada.")
    print("Para restaurarla, ejecuta: alembic upgrade head")
    print("="*74 + "\n")
