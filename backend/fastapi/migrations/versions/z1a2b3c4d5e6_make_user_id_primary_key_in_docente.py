"""Make user_id primary key in docente table and update foreign keys

Revision ID: z1a2b3c4d5e6
Revises: v5w6x7y8z9a0
Create Date: 2025-11-18 00:00:00.000000

Esta migración realiza un cambio arquitectónico importante:
1. Elimina el campo 'id' autoincremental de la tabla docente
2. Convierte 'user_id' en la clave primaria
3. Actualiza todas las foreign keys en tablas relacionadas:
   - clase.docente_id → clase.docente_id (ahora apunta a docente.user_id)
   - restriccion.docente_id → restriccion.docente_id (ahora apunta a docente.user_id)
   - restriccion_horario.docente_id → restriccion_horario.docente_id (ahora apunta a docente.user_id)
   - evento.docente_id → evento.docente_id (ahora apunta a docente.user_id)

IMPORTANTE: Esta migración preserva los datos existentes mapeando:
  docente.id (viejo) → user_id (nuevo identificador)

Beneficios:
- Elimina confusión entre docente.id y user.id
- Simplifica queries (docente_id == user_id)
- Mantiene relación 1:1 estricta entre User y Docente
- Reduce redundancia en la base de datos
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'z1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'v5w6x7y8z9a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convertir user_id en PK de docente y actualizar todas las FKs.
    
    Proceso:
    1. Crear tabla temporal con nueva estructura
    2. Copiar datos mapeando docente.id → docente.user_id en FKs
    3. Eliminar tabla original
    4. Renombrar tabla temporal a docente
    """
    bind = op.get_bind()
    
    print("\n" + "="*80)
    print("🔄 INICIANDO MIGRACIÓN: user_id como PK en tabla docente")
    print("="*80 + "\n")
    
    # ========================================================================
    # PASO 1: Verificar integridad de datos antes de migrar
    # ========================================================================
    print("🔍 PASO 1: Verificando integridad de datos...\n")
    
    # Verificar que no existan docentes sin user_id
    result = bind.execute(sa.text("SELECT COUNT(*) FROM docente WHERE user_id IS NULL"))
    docentes_sin_user = result.scalar()
    
    if docentes_sin_user > 0:
        raise Exception(f"""
╔════════════════════════════════════════════════════════════════════════╗
║  ⚠️  ERROR: {docentes_sin_user} docentes sin user_id                             ║
╚════════════════════════════════════════════════════════════════════════╝

No se puede continuar con la migración porque existen docentes sin user_id.
Esto no debería ocurrir si la migración anterior se ejecutó correctamente.

SOLUCIÓN:
1. Revisar y corregir los datos manualmente
2. Asegurar que todos los docentes tengan un user_id válido
""")
    
    print("  ✓ Todos los docentes tienen user_id válido\n")
    
    # ========================================================================
    # PASO 2: Eliminar constraints y FKs de tablas relacionadas
    # ========================================================================
    print("🔧 PASO 2: Eliminando constraints existentes...\n")
    
    # Tabla: clase
    print("  📋 Procesando tabla: clase")
    with op.batch_alter_table('clase', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('clase_docente_id_fkey', type_='foreignkey')
            print("    ✓ FK clase_docente_id_fkey eliminada")
        except Exception as e:
            print(f"    ⚠️  FK clase_docente_id_fkey no existe: {e}")
    
    # Tabla: restriccion
    print("  📋 Procesando tabla: restriccion")
    with op.batch_alter_table('restriccion', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('restriccion_docente_id_fkey', type_='foreignkey')
            print("    ✓ FK restriccion_docente_id_fkey eliminada")
        except Exception as e:
            print(f"    ⚠️  FK restriccion_docente_id_fkey no existe: {e}")
    
    # Tabla: restriccion_horario
    print("  📋 Procesando tabla: restriccion_horario")
    with op.batch_alter_table('restriccion_horario', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('restriccion_horario_docente_id_fkey', type_='foreignkey')
            print("    ✓ FK restriccion_horario_docente_id_fkey eliminada")
        except Exception as e:
            print(f"    ⚠️  FK restriccion_horario_docente_id_fkey no existe: {e}")
    
    # Tabla: evento
    print("  📋 Procesando tabla: evento")
    with op.batch_alter_table('evento', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('evento_docente_id_fkey', type_='foreignkey')
            print("    ✓ FK evento_docente_id_fkey eliminada")
        except Exception as e:
            print(f"    ⚠️  FK evento_docente_id_fkey no existe: {e}")
    
    print()
    
    # ========================================================================
    # PASO 3: Actualizar valores de docente_id en tablas relacionadas
    # ========================================================================
    print("🔄 PASO 3: Actualizando docente_id en tablas relacionadas...\n")
    print("  (Mapeando: docente.id → docente.user_id)\n")
    
    # Actualizar clase.docente_id
    print("  📋 Actualizando tabla: clase")
    bind.execute(sa.text("""
        UPDATE clase 
        SET docente_id = (SELECT user_id FROM docente WHERE docente.id = clase.docente_id)
        WHERE docente_id IS NOT NULL
    """))
    result = bind.execute(sa.text("SELECT COUNT(*) FROM clase WHERE docente_id IS NOT NULL"))
    count = result.scalar()
    print(f"    ✓ {count} registros actualizados\n")
    
    # Actualizar restriccion.docente_id
    print("  📋 Actualizando tabla: restriccion")
    bind.execute(sa.text("""
        UPDATE restriccion 
        SET docente_id = (SELECT user_id FROM docente WHERE docente.id = restriccion.docente_id)
        WHERE docente_id IS NOT NULL
    """))
    result = bind.execute(sa.text("SELECT COUNT(*) FROM restriccion WHERE docente_id IS NOT NULL"))
    count = result.scalar()
    print(f"    ✓ {count} registros actualizados\n")
    
    # Actualizar restriccion_horario.docente_id
    print("  📋 Actualizando tabla: restriccion_horario")
    bind.execute(sa.text("""
        UPDATE restriccion_horario 
        SET docente_id = (SELECT user_id FROM docente WHERE docente.id = restriccion_horario.docente_id)
        WHERE docente_id IS NOT NULL
    """))
    result = bind.execute(sa.text("SELECT COUNT(*) FROM restriccion_horario WHERE docente_id IS NOT NULL"))
    count = result.scalar()
    print(f"    ✓ {count} registros actualizados\n")
    
    # Actualizar evento.docente_id
    print("  📋 Actualizando tabla: evento")
    bind.execute(sa.text("""
        UPDATE evento 
        SET docente_id = (SELECT user_id FROM docente WHERE docente.id = evento.docente_id)
        WHERE docente_id IS NOT NULL
    """))
    result = bind.execute(sa.text("SELECT COUNT(*) FROM evento WHERE docente_id IS NOT NULL"))
    count = result.scalar()
    print(f"    ✓ {count} registros actualizados\n")
    
    # ========================================================================
    # PASO 4: Recrear tabla docente con nueva estructura
    # ========================================================================
    print("🏗️  PASO 4: Recreando tabla docente con nueva estructura...\n")
    
    # Crear tabla temporal con nueva estructura
    print("  📋 Creando tabla temporal: docente_new")
    op.create_table('docente_new',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('departamento', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    print("    ✓ Tabla temporal creada\n")
    
    # Copiar datos de docente a docente_new
    print("  📋 Copiando datos a tabla temporal")
    bind.execute(sa.text("""
        INSERT INTO docente_new (user_id, departamento)
        SELECT user_id, departamento FROM docente
    """))
    result = bind.execute(sa.text("SELECT COUNT(*) FROM docente_new"))
    count = result.scalar()
    print(f"    ✓ {count} registros copiados\n")
    
    # Eliminar tabla original
    print("  📋 Eliminando tabla original: docente")
    op.drop_table('docente')
    print("    ✓ Tabla original eliminada\n")
    
    # Renombrar tabla temporal
    print("  📋 Renombrando tabla temporal: docente_new → docente")
    op.rename_table('docente_new', 'docente')
    print("    ✓ Tabla renombrada\n")
    
    # ========================================================================
    # PASO 5: Recrear foreign keys en tablas relacionadas
    # ========================================================================
    print("🔗 PASO 5: Recreando foreign keys...\n")
    
    # Tabla: clase
    print("  📋 Procesando tabla: clase")
    with op.batch_alter_table('clase', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'clase_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['user_id'],
            ondelete='CASCADE'
        )
    print("    ✓ FK clase.docente_id → docente.user_id creada\n")
    
    # Tabla: restriccion
    print("  📋 Procesando tabla: restriccion")
    with op.batch_alter_table('restriccion', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'restriccion_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['user_id'],
            ondelete='CASCADE'
        )
    print("    ✓ FK restriccion.docente_id → docente.user_id creada\n")
    
    # Tabla: restriccion_horario
    print("  📋 Procesando tabla: restriccion_horario")
    with op.batch_alter_table('restriccion_horario', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'restriccion_horario_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['user_id'],
            ondelete='CASCADE'
        )
    print("    ✓ FK restriccion_horario.docente_id → docente.user_id creada\n")
    
    # Tabla: evento
    print("  📋 Procesando tabla: evento")
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'evento_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['user_id'],
            ondelete='CASCADE'
        )
    print("    ✓ FK evento.docente_id → docente.user_id creada\n")
    
    # ========================================================================
    # FINALIZACIÓN
    # ========================================================================
    print("="*80)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80)
    print("\nCambios aplicados:")
    print("  ✓ docente.id eliminado (campo autoincremental)")
    print("  ✓ docente.user_id ahora es PRIMARY KEY")
    print("  ✓ clase.docente_id → docente.user_id")
    print("  ✓ restriccion.docente_id → docente.user_id")
    print("  ✓ restriccion_horario.docente_id → docente.user_id")
    print("  ✓ evento.docente_id → docente.user_id")
    print("\nArquitectura simplificada:")
    print("  • Un docente = un user_id (sin IDs duplicados)")
    print("  • docente_id en tablas relacionadas == user_id del docente")
    print("  • Relación 1:1 estricta garantizada")
    print("="*80 + "\n")


def downgrade() -> None:
    """
    Revertir cambios: volver a estructura con docente.id autoincremental.
    
    ADVERTENCIA: Este downgrade es complejo y puede causar pérdida de datos
    si no se maneja correctamente. Solo usar en emergencias.
    """
    bind = op.get_bind()
    
    print("\n" + "="*80)
    print("⚠️  REVERTIENDO MIGRACIÓN: Restaurando docente.id")
    print("="*80 + "\n")
    
    # ========================================================================
    # PASO 1: Eliminar FKs actuales
    # ========================================================================
    print("🔧 PASO 1: Eliminando foreign keys actuales...\n")
    
    with op.batch_alter_table('evento', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('evento_docente_id_fkey', type_='foreignkey')
        except:
            pass
    
    with op.batch_alter_table('restriccion_horario', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('restriccion_horario_docente_id_fkey', type_='foreignkey')
        except:
            pass
    
    with op.batch_alter_table('restriccion', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('restriccion_docente_id_fkey', type_='foreignkey')
        except:
            pass
    
    with op.batch_alter_table('clase', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('clase_docente_id_fkey', type_='foreignkey')
        except:
            pass
    
    print("  ✓ Foreign keys eliminadas\n")
    
    # ========================================================================
    # PASO 2: Recrear tabla docente con estructura original
    # ========================================================================
    print("🏗️  PASO 2: Recreando tabla docente con id autoincremental...\n")
    
    # Crear tabla temporal con estructura original
    op.create_table('docente_old',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('departamento', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_docente_user_id')
    )
    
    # Copiar datos (user_id se convierte en nuevo id autoincremental)
    bind.execute(sa.text("""
        INSERT INTO docente_old (user_id, departamento)
        SELECT user_id, departamento FROM docente
    """))
    
    # Crear mapeo temporal: user_id → nuevo id
    result = bind.execute(sa.text("""
        SELECT id, user_id FROM docente_old
    """))
    mapeo = {row[1]: row[0] for row in result.fetchall()}
    
    # Eliminar tabla actual y renombrar
    op.drop_table('docente')
    op.rename_table('docente_old', 'docente')
    
    print("  ✓ Tabla docente recreada con id autoincremental\n")
    
    # ========================================================================
    # PASO 3: Actualizar docente_id en tablas relacionadas
    # ========================================================================
    print("🔄 PASO 3: Actualizando docente_id en tablas relacionadas...\n")
    
    # Actualizar usando el mapeo
    for user_id, new_id in mapeo.items():
        bind.execute(sa.text(f"""
            UPDATE clase SET docente_id = {new_id} WHERE docente_id = {user_id}
        """))
        bind.execute(sa.text(f"""
            UPDATE restriccion SET docente_id = {new_id} WHERE docente_id = {user_id}
        """))
        bind.execute(sa.text(f"""
            UPDATE restriccion_horario SET docente_id = {new_id} WHERE docente_id = {user_id}
        """))
        bind.execute(sa.text(f"""
            UPDATE evento SET docente_id = {new_id} WHERE docente_id = {user_id}
        """))
    
    print("  ✓ IDs actualizados en tablas relacionadas\n")
    
    # ========================================================================
    # PASO 4: Recrear FKs originales
    # ========================================================================
    print("🔗 PASO 4: Recreando foreign keys originales...\n")
    
    with op.batch_alter_table('clase', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'clase_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['id']
        )
    
    with op.batch_alter_table('restriccion', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'restriccion_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['id']
        )
    
    with op.batch_alter_table('restriccion_horario', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'restriccion_horario_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['id']
        )
    
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'evento_docente_id_fkey',
            'docente',
            ['docente_id'],
            ['id']
        )
    
    print("  ✓ Foreign keys recreadas\n")
    
    print("="*80)
    print("⚠️  DOWNGRADE COMPLETADO")
    print("="*80)
    print("\nEstructura restaurada:")
    print("  • docente.id (autoincremental) restaurado como PK")
    print("  • docente.user_id como FK única a user")
    print("  • Todas las FKs apuntan nuevamente a docente.id")
    print("\nNOTA: Los IDs pueden haber cambiado. Verificar integridad.")
    print("="*80 + "\n")
