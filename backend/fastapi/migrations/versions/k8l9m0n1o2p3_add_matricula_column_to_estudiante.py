"""Add matricula column to estudiante table with auto-generation

Revision ID: k8l9m0n1o2p3
Revises: e2f3g4h5i6j7
Create Date: 2025-11-15 18:00:00.000000

Esta migración agrega la columna 'matricula' a la tabla 'estudiante' y
la puebla automáticamente para estudiantes existentes.

Formato de matrícula: {AÑO}{USER_ID:06d}
Ejemplo: Usuario con ID 2 en 2025 → "2025000002"
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'k8l9m0n1o2p3'
down_revision: Union[str, Sequence[str], None] = 'e2f3g4h5i6j7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Agregar columna matricula a la tabla estudiante y poblarla automáticamente.
    """
    print("\n" + "="*74)
    print("🎓 AGREGANDO COLUMNA MATRÍCULA A ESTUDIANTES")
    print("="*74)
    
    # Obtener conexión para poblar datos
    bind = op.get_bind()
    
    # ========================================================================
    # PASO 1: Verificar si la columna ya existe, si no, agregarla
    # ========================================================================
    print("\n📋 Paso 1: Verificando/agregando columna matricula...")
    
    # Verificar si la columna ya existe
    result = bind.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='estudiante' AND column_name='matricula'
    """))
    columna_existe = result.fetchone() is not None
    
    if not columna_existe:
        print("  ℹ️  Columna no existe, agregando...")
        with op.batch_alter_table('estudiante', schema=None) as batch_op:
            batch_op.add_column(sa.Column('matricula', sa.Text(), nullable=True))
        print("  ✓ Columna agregada (temporalmente nullable)")
    else:
        print("  ✓ Columna ya existe, continuando...")
    
    # ========================================================================
    # PASO 2: Poblar matrículas para estudiantes existentes
    # ========================================================================
    print("\n📝 Paso 2: Generando matrículas para estudiantes existentes...")
    
    # Obtener año actual
    current_year = datetime.now().year
    
    # Obtener todos los estudiantes existentes
    result = bind.execute(sa.text("SELECT id, user_id FROM estudiante"))
    estudiantes = result.fetchall()
    
    if estudiantes:
        print(f"  📊 Se encontraron {len(estudiantes)} estudiantes")
        
        # Generar y actualizar matrícula para cada estudiante
        for estudiante in estudiantes:
            estudiante_id = estudiante[0]
            user_id = estudiante[1]
            
            # Generar matrícula: {AÑO}{USER_ID:06d}
            matricula = f"{current_year}{user_id:06d}"
            
            # Actualizar registro
            bind.execute(
                sa.text("UPDATE estudiante SET matricula = :matricula WHERE id = :id"),
                {"matricula": matricula, "id": estudiante_id}
            )
            print(f"    ✓ Estudiante {estudiante_id} (user_id={user_id}): matrícula = {matricula}")
        
        print(f"  ✅ {len(estudiantes)} matrículas generadas exitosamente")
    else:
        print("  ℹ️  No hay estudiantes existentes para actualizar")
    
    # ========================================================================
    # PASO 3: Verificar que todas las matrículas estén pobladas
    # ========================================================================
    print("\n🔍 Paso 3: Verificando integridad de datos...")
    
    result = bind.execute(sa.text("SELECT COUNT(*) FROM estudiante WHERE matricula IS NULL"))
    matriculas_null = result.scalar()
    
    if matriculas_null > 0:
        error_msg = f"""
╔═════════════════════════════════════════════════════════════════╗
║  ⚠️  ERROR: EXISTEN {matriculas_null} ESTUDIANTES SIN MATRÍCULA       ║
╚═════════════════════════════════════════════════════════════════╝

No se pudo generar la matrícula para todos los estudiantes.
Por favor, revisa los datos manualmente.
"""
        raise Exception(error_msg)
    
    print("  ✓ Todas las matrículas fueron generadas correctamente")
    
    # ========================================================================
    # PASO 4: Agregar constraints NOT NULL y UNIQUE (si no existen)
    # ========================================================================
    print("\n🔒 Paso 4: Agregando constraints de integridad...")
    
    # Verificar si el constraint UNIQUE ya existe
    result = bind.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name='estudiante' AND constraint_name='uq_estudiante_matricula'
    """))
    unique_existe = result.fetchone() is not None
    
    with op.batch_alter_table('estudiante', schema=None) as batch_op:
        # Hacer la columna NOT NULL
        batch_op.alter_column('matricula',
                            existing_type=sa.Text(),
                            nullable=False)
        print("  ✓ NOT NULL constraint aplicado")
        
        # Agregar constraint UNIQUE solo si no existe
        if not unique_existe:
            batch_op.create_unique_constraint('uq_estudiante_matricula', ['matricula'])
            print("  ✓ UNIQUE constraint agregado")
        else:
            print("  ✓ UNIQUE constraint ya existe")
    
    print("\n" + "="*74)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*74)
    print("\nColumna 'matricula' agregada con éxito:")
    print("  ✓ Tipo: TEXT")
    print("  ✓ Nullable: NO (NOT NULL)")
    print("  ✓ Unique: SÍ (UNIQUE)")
    print(f"  ✓ Formato: {{AÑO}}{{USER_ID:06d}} (ej: {current_year}000002)")
    if estudiantes:
        print(f"  ✓ Registros actualizados: {len(estudiantes)}")
    print("\nLas matrículas futuras se generarán automáticamente en el backend. ✨")
    print("="*74 + "\n")


def downgrade() -> None:
    """
    Revertir la adición de la columna matricula.
    
    ADVERTENCIA: Esto eliminará TODAS las matrículas de la base de datos.
    """
    print("\n" + "="*74)
    print("⚠️  REVERTIENDO COLUMNA MATRÍCULA (DOWNGRADE)")
    print("="*74)
    
    # Obtener conexión para verificar
    bind = op.get_bind()
    result = bind.execute(sa.text("SELECT COUNT(*) FROM estudiante"))
    total_estudiantes = result.scalar()
    
    print(f"\n⚠️  ADVERTENCIA: Se eliminarán las matrículas de {total_estudiantes} estudiantes")
    
    # Eliminar constraint UNIQUE primero
    print("\n🔓 Paso 1: Removiendo constraints...")
    with op.batch_alter_table('estudiante', schema=None) as batch_op:
        batch_op.drop_constraint('uq_estudiante_matricula', type_='unique')
        print("  ✓ UNIQUE constraint removido")
    
    # Eliminar la columna
    print("\n🗑️  Paso 2: Eliminando columna matricula...")
    with op.batch_alter_table('estudiante', schema=None) as batch_op:
        batch_op.drop_column('matricula')
        print("  ✓ Columna eliminada")
    
    print("\n" + "="*74)
    print("⚠️  DOWNGRADE COMPLETADO")
    print("="*74)
    print("\nLa columna 'matricula' ha sido eliminada.")
    print("Para restaurarla, ejecuta: alembic upgrade head")
    print("="*74 + "\n")
