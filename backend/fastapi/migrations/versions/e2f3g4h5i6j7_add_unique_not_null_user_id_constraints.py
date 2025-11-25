"""Add UNIQUE and NOT NULL constraints to user_id in role tables

Revision ID: e2f3g4h5i6j7
Revises: d11e5845cfe7
Create Date: 2025-11-15 16:00:00.000000

IMPORTANTE: Esta migración requiere que se ejecute el script de limpieza
de registros huérfanos ANTES de aplicarse:
    docker exec sgh-backend python scripts/check_orphan_records.py --clean

Esta migración agrega constraints críticos de integridad:
1. UNIQUE(user_id) - Previene duplicados, garantiza relación 1:1
2. NOT NULL - Previene registros huérfanos sin usuario asociado

Estos constraints aseguran que:
- Un usuario solo puede tener UN registro de docente/estudiante/administrador
- Todos los registros de roles deben tener un usuario válido asociado
- Se previenen inconsistencias en la base de datos
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f3g4h5i6j7'
down_revision: Union[str, Sequence[str], None] = 'd11e5845cfe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Agregar constraints UNIQUE y NOT NULL a user_id en tablas de roles.
    
    PRECONDICIÓN: No deben existir registros con user_id NULL ni duplicados.
    Si la migración falla, ejecutar primero:
        docker exec sgh-backend python scripts/check_orphan_records.py --clean
    """
    # Obtener conexión para verificar datos
    bind = op.get_bind()
    
    # ========================================================================
    # PASO 1: Verificar que no existan registros huérfanos (user_id NULL)
    # ========================================================================
    print("\n🔍 Verificando registros huérfanos...")
    
    # Verificar docentes
    result = bind.execute(sa.text("SELECT COUNT(*) FROM docente WHERE user_id IS NULL"))
    docentes_huerfanos = result.scalar()
    
    # Verificar estudiantes
    result = bind.execute(sa.text("SELECT COUNT(*) FROM estudiante WHERE user_id IS NULL"))
    estudiantes_huerfanos = result.scalar()
    
    # Verificar administradores
    result = bind.execute(sa.text("SELECT COUNT(*) FROM administrador WHERE user_id IS NULL"))
    admins_huerfanos = result.scalar()
    
    total_huerfanos = docentes_huerfanos + estudiantes_huerfanos + admins_huerfanos
    
    if total_huerfanos > 0:
        error_msg = f"""
╔════════════════════════════════════════════════════════════════════════╗
║  ⚠️  ERROR: EXISTEN {total_huerfanos} REGISTROS HUÉRFANOS EN LA BASE DE DATOS  ║
╚════════════════════════════════════════════════════════════════════════╝

Se encontraron registros con user_id NULL:
  - Docentes:        {docentes_huerfanos}
  - Estudiantes:     {estudiantes_huerfanos}
  - Administradores: {admins_huerfanos}

SOLUCIÓN:
1. Revisar los registros huérfanos:
   docker exec sgh-backend python scripts/check_orphan_records.py --check

2. Limpiar los registros huérfanos:
   docker exec sgh-backend python scripts/check_orphan_records.py --clean

3. Volver a ejecutar la migración:
   docker exec sgh-backend alembic upgrade head

NOTA: Esta migración NO eliminará datos automáticamente por seguridad.
"""
        raise Exception(error_msg)
    
    print(f"  ✓ No se encontraron registros huérfanos")
    
    # ========================================================================
    # PASO 2: Verificar que no existan duplicados de user_id
    # ========================================================================
    print("\n🔍 Verificando duplicados...")
    
    # Verificar duplicados en docentes
    result = bind.execute(sa.text("""
        SELECT user_id, COUNT(*) as count 
        FROM docente 
        WHERE user_id IS NOT NULL 
        GROUP BY user_id 
        HAVING COUNT(*) > 1
    """))
    docentes_duplicados = result.fetchall()
    
    # Verificar duplicados en estudiantes
    result = bind.execute(sa.text("""
        SELECT user_id, COUNT(*) as count 
        FROM estudiante 
        WHERE user_id IS NOT NULL 
        GROUP BY user_id 
        HAVING COUNT(*) > 1
    """))
    estudiantes_duplicados = result.fetchall()
    
    # Verificar duplicados en administradores
    result = bind.execute(sa.text("""
        SELECT user_id, COUNT(*) as count 
        FROM administrador 
        WHERE user_id IS NOT NULL 
        GROUP BY user_id 
        HAVING COUNT(*) > 1
    """))
    admins_duplicados = result.fetchall()
    
    if docentes_duplicados or estudiantes_duplicados or admins_duplicados:
        error_msg = f"""
╔══════════════════════════════════════════════════════════════════════╗
║  ⚠️  ERROR: EXISTEN REGISTROS DUPLICADOS EN LA BASE DE DATOS       ║
╚══════════════════════════════════════════════════════════════════════╝

Se encontraron user_id duplicados:
"""
        if docentes_duplicados:
            error_msg += f"\nDocentes duplicados:\n"
            for row in docentes_duplicados:
                error_msg += f"  - user_id {row[0]}: {row[1]} registros\n"
        
        if estudiantes_duplicados:
            error_msg += f"\nEstudiantes duplicados:\n"
            for row in estudiantes_duplicados:
                error_msg += f"  - user_id {row[0]}: {row[1]} registros\n"
        
        if admins_duplicados:
            error_msg += f"\nAdministradores duplicados:\n"
            for row in admins_duplicados:
                error_msg += f"  - user_id {row[0]}: {row[1]} registros\n"
        
        error_msg += """
SOLUCIÓN:
Debes resolver manualmente los duplicados antes de continuar.
Revisa cuál registro es el correcto y elimina los duplicados.
"""
        raise Exception(error_msg)
    
    print(f"  ✓ No se encontraron duplicados")
    
    # ========================================================================
    # PASO 3: Agregar constraints UNIQUE y NOT NULL
    # ========================================================================
    print("\n✨ Agregando constraints de integridad...")
    
    # DOCENTE
    print("  📋 Tabla: docente")
    with op.batch_alter_table('docente', schema=None) as batch_op:
        # Primero agregar UNIQUE
        batch_op.create_unique_constraint('uq_docente_user_id', ['user_id'])
        print("    ✓ UNIQUE constraint agregado")
        
        # Luego agregar NOT NULL
        batch_op.alter_column('user_id',
                            existing_type=sa.INTEGER(),
                            nullable=False)
        print("    ✓ NOT NULL constraint agregado")
    
    # ESTUDIANTE
    print("  📋 Tabla: estudiante")
    with op.batch_alter_table('estudiante', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_estudiante_user_id', ['user_id'])
        print("    ✓ UNIQUE constraint agregado")
        
        batch_op.alter_column('user_id',
                            existing_type=sa.INTEGER(),
                            nullable=False)
        print("    ✓ NOT NULL constraint agregado")
    
    # ADMINISTRADOR
    print("  📋 Tabla: administrador")
    with op.batch_alter_table('administrador', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_administrador_user_id', ['user_id'])
        print("    ✓ UNIQUE constraint agregado")
        
        batch_op.alter_column('user_id',
                            existing_type=sa.INTEGER(),
                            nullable=False)
        print("    ✓ NOT NULL constraint agregado")
    
    print("\n" + "="*74)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*74)
    print("\nConstraints agregados:")
    print("  ✓ docente.user_id      → UNIQUE + NOT NULL")
    print("  ✓ estudiante.user_id   → UNIQUE + NOT NULL")
    print("  ✓ administrador.user_id → UNIQUE + NOT NULL")
    print("\nIntegridad referencial garantizada. ✨")
    print("="*74 + "\n")


def downgrade() -> None:
    """
    Revertir constraints UNIQUE y NOT NULL de user_id.
    
    ADVERTENCIA: Esto permite registros huérfanos y duplicados nuevamente.
    Solo usar en caso de emergencia.
    """
    print("\n⚠️  REVERTIENDO CONSTRAINTS (DOWNGRADE)...\n")
    
    # ADMINISTRADOR
    print("  📋 Tabla: administrador")
    with op.batch_alter_table('administrador', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                            existing_type=sa.INTEGER(),
                            nullable=True)
        print("    ✓ NOT NULL constraint removido")
        
        batch_op.drop_constraint('uq_administrador_user_id', type_='unique')
        print("    ✓ UNIQUE constraint removido")
    
    # ESTUDIANTE
    print("  📋 Tabla: estudiante")
    with op.batch_alter_table('estudiante', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                            existing_type=sa.INTEGER(),
                            nullable=True)
        print("    ✓ NOT NULL constraint removido")
        
        batch_op.drop_constraint('uq_estudiante_user_id', type_='unique')
        print("    ✓ UNIQUE constraint removido")
    
    # DOCENTE
    print("  📋 Tabla: docente")
    with op.batch_alter_table('docente', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                            existing_type=sa.INTEGER(),
                            nullable=True)
        print("    ✓ NOT NULL constraint removido")
        
        batch_op.drop_constraint('uq_docente_user_id', type_='unique')
        print("    ✓ UNIQUE constraint removido")
    
    print("\n" + "="*74)
    print("⚠️  DOWNGRADE COMPLETADO")
    print("="*74)
    print("\nADVERTENCIA: La base de datos ya NO tiene protección contra:")
    print("  ⚠️  Registros huérfanos (user_id NULL)")
    print("  ⚠️  Registros duplicados (mismo user_id)")
    print("\nSe recomienda volver a aplicar la migración lo antes posible.")
    print("="*74 + "\n")
