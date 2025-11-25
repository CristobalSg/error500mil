# SGH — Notas rápidas

- **Levantar backend y mobile**  
  `docker compose --env-file .env up -d postgres backend mobile`

- **Rebuild backend (incluye scripts y seeds nuevos)**  
  `docker compose --env-file .env up -d --build backend`

- **Seed de datos base (asignaturas, docentes, secciones)**  
  ```bash
  docker compose --env-file .env exec backend \
    sh -c "cd /app && python scripts/seed_data.py \
      --asignaturas data/asignaturas.csv \
      --docentes data/docentes.csv \
      --secciones data/secciones.csv \
      --seccion-asignatura-id 1 \
      --seccion-semestre 1 \
      --docente-password SeedDocente#2025"
  ```
  - Usa `DOCENTE_SEED_PASSWORD` si quieres otro password.
  - `SEED_DATA=true` en el entorno hará que `start.sh` ejecute el seed al arrancar.

- **Preview del payload que se envía al agente (sin generar)**  
  `GET /api/timetable/generate/preview?semester=2025-1&institution_name=Depto%20Informatica`  
  Requiere permiso `SYSTEM_CONFIG`.

- **Mapping docente–asignatura–grupo para activities**  
  Archivo: `backend/fastapi/data/docente_asignaturas.csv`  
  Campos: `group_id, teacher_email, subject_slug, subject_code, duration, total_duration, comments, active`

- **Datos semilla**  
  - Asignaturas: `data/asignaturas.csv`  
  - Docentes: `data/docentes.csv`  
  - Secciones: `data/secciones.csv`  
  - Mapping actividades: `data/docente_asignaturas.csv`
