# Guía de Uso del Makefile de Testing y Seguridad

Este documento describe cómo usar el `Makefile.tests` para ejecutar pruebas, análisis de seguridad y comprobaciones de calidad de código en el backend de SGH.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación de Herramientas](#instalación-de-herramientas)
- [Comandos de Pruebas](#comandos-de-pruebas)
- [Análisis de Seguridad](#análisis-de-seguridad)
- [Linting y Formateo](#linting-y-formateo)
- [Pipeline CI/CD](#pipeline-cicd)
- [Comandos Docker](#comandos-docker)

## 🔧 Requisitos Previos

### Para ejecución local:
```bash
# Tener Python 3.12+ instalado
python --version

# Estar en el directorio del backend
cd backend/fastapi
```

### Para ejecución con Docker:
```bash
# Docker y Docker Compose instalados
docker --version
docker compose version

# Variables de entorno configuradas
# El archivo .env.development debe estar en la raíz del proyecto
```

## 📦 Instalación de Herramientas

### Instalación completa (todas las herramientas):
```bash
make install-all
```

### Instalación por categoría:
```bash
# Solo herramientas de testing
make install-test

# Solo herramientas de seguridad
make install-security

# Solo herramientas de linting
make install-lint
```

## 🧪 Comandos de Pruebas

### Ejecución Local

```bash
# Ver todos los comandos disponibles
make help

# Ejecutar todas las pruebas
make test

# Ejecutar pruebas con salida verbose
make test-verbose

# Ejecutar pruebas con reporte de cobertura
make test-cov

# Ejecutar pruebas con reporte HTML de cobertura
make test-cov-html

# Ejecutar solo pruebas unitarias
make test-unit

# Ejecutar solo pruebas de integración
make test-integration
```

### Pruebas Específicas

```bash
# Pruebas por módulo
make test-docente
make test-asignatura
make test-clase
make test-restriccion
make test-auth

# Pruebas de API
make test-auth-api
make test-restricciones-api
make test-main-api
```

### Ejecución en Docker

```bash
# Ejecutar todas las pruebas en Docker
make docker-test

# Ejecutar pruebas con cobertura en Docker
make docker-test-cov

# Ejecutar pruebas verbose en Docker
make docker-test-verbose
```

**Nota importante**: Los comandos Docker automáticamente usan el archivo `.env.development` y `docker-compose.dev.yml` configurados en el Makefile.

## 🔒 Análisis de Seguridad

### Herramientas de Seguridad

#### Bandit - Análisis de vulnerabilidades de código
```bash
# Ejecutar Bandit
make security-bandit

# Genera:
# - bandit-report.json: Reporte detallado en JSON
# - Salida en consola con resultados
```

#### Safety - Verificación de vulnerabilidades en dependencias
```bash
# Ejecutar Safety
make security-safety

# Verifica vulnerabilidades conocidas en las dependencias
```

#### pip-audit - Auditoría de paquetes Python
```bash
# Ejecutar pip-audit
make security-deps

# Genera:
# - bandit-audit.json: Reporte de auditoría
# - Salida en consola
```

#### detect-secrets - Detección de secretos hardcodeados
```bash
# Ejecutar detect-secrets
make security-secrets

# Usa .secrets.baseline como referencia
```

#### Análisis completo de seguridad
```bash
# Ejecutar todos los análisis de seguridad
make security-all

# Ejecutar análisis de seguridad en Docker
make docker-security
```

### Interpretación de Resultados

**Bandit**: Reporta problemas de seguridad con niveles de severidad:
- **HIGH**: Vulnerabilidades críticas que deben ser corregidas inmediatamente
- **MEDIUM**: Problemas de seguridad que deben ser revisados
- **LOW**: Mejoras de seguridad recomendadas

**Safety**: Lista CVEs conocidos en las dependencias con enlaces a detalles.

**pip-audit**: Similar a Safety, pero con análisis más detallado de la cadena de dependencias.

## 🔍 Linting y Formateo

### Linting (Verificación de Código)

```bash
# Ejecutar todos los linters
make lint-all

# Linters individuales
make lint-flake8    # Estilo de código PEP 8
make lint-pylint    # Análisis estático avanzado
make lint-mypy      # Verificación de tipos
make lint-black     # Verificación de formato
make lint-isort     # Verificación de imports

# En Docker
make docker-lint
```

### Formateo (Corrección Automática)

```bash
# Formatear todo el código
make format-all

# Formateo individual
make format-black   # Formatear con Black
make format-isort   # Ordenar imports

# En Docker
make docker-format
```

### Configuraciones de Linting

Las herramientas usan estos archivos de configuración:
- **Flake8**: `.flake8`
- **Pylint**: `.pylintrc`
- **MyPy**: `mypy.ini`
- **Black/isort**: `pyproject.toml`

## 🚀 Pipeline CI/CD

### Pipeline Completo

```bash
# Ejecutar pipeline CI completo (lint + security + test)
make ci-pipeline

# Etapas:
# 1. Linting completo
# 2. Análisis de seguridad
# 3. Tests con cobertura
```

### Pipeline por Etapas

```bash
# Solo linting
make ci-lint

# Solo seguridad
make ci-security

# Solo tests
make ci-test
```

### Pipeline en Docker

```bash
# Pipeline completo en Docker
make docker-ci-pipeline
```

## 🐳 Comandos Docker

Todos los comandos Docker están preconfigurados para usar:
- Archivo de variables: `../../.env.development`
- Compose file: `../../docker-compose.dev.yml`
- Servicio: `backend`

### Estructura del Comando Docker

Los comandos internamente ejecutan:
```bash
docker compose --env-file ../../.env.development -f ../../docker-compose.dev.yml exec backend <comando>
```

### Comandos Disponibles

```bash
# Tests
make docker-test
make docker-test-cov
make docker-test-verbose

# Seguridad
make docker-security

# Linting
make docker-lint

# Formateo
make docker-format

# Pipeline completo
make docker-ci-pipeline
```

## 📊 Reportes Generados

### Archivos de Reporte

```
backend/fastapi/
├── htmlcov/                    # Reporte HTML de cobertura de tests
├── coverage.xml                # Reporte XML de cobertura
├── .coverage                   # Datos de cobertura (binario)
├── bandit-report.json          # Reporte de Bandit
├── bandit-audit.json           # Reporte de pip-audit
└── .mypy_cache/                # Cache de MyPy
```

### Limpiar Reportes

```bash
# Limpiar archivos de cobertura
make clean-cov
```

## 🔄 Workflow Recomendado

### Durante el Desarrollo

1. **Antes de commit**:
   ```bash
   make format-all     # Formatear código
   make lint-all       # Verificar linting
   make test          # Ejecutar tests
   ```

2. **Revisión de seguridad periódica**:
   ```bash
   make security-all
   ```

### En CI/CD

```bash
# En el pipeline de integración continua
make ci-pipeline
```

### Desarrollo con Docker

```bash
# Levantar el entorno
cd ../../
docker compose --env-file .env.development -f docker-compose.dev.yml up -d

# Ejecutar tests
cd backend/fastapi
make docker-test

# Ver logs
docker compose --env-file ../../.env.development -f ../../docker-compose.dev.yml logs -f backend
```

## ⚙️ Configuración Personalizada

### Variables de Entorno

Las variables se configuran en `.env.development`:
```env
POSTGRES_DB=SGH
POSTGRES_USER=sgh_admin
POSTGRES_PASSWORD=...
JWT_SECRET_KEY=...
# etc.
```

### Personalizar Comandos

Puedes modificar el `Makefile.tests` para:
- Cambiar niveles de severidad
- Ajustar rutas de análisis
- Modificar flags de comandos
- Agregar nuevas herramientas

## 🐛 Solución de Problemas

### Error: "Command not found"

```bash
# Instalar herramientas faltantes
make install-all
```

### Error: "No module named 'X'"

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error en Docker: "Container not running"

```bash
# Levantar el entorno
cd ../../
docker compose --env-file .env.development -f docker-compose.dev.yml up -d backend
```

### Permisos en Linux

```bash
# Si hay problemas de permisos con archivos generados en Docker
sudo chown -R $USER:$USER htmlcov/ *.json .mypy_cache/
```

## 📚 Referencias

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pylint Documentation](https://pylint.pycqa.org/)

## 📝 Notas Adicionales

- Los comandos de formateo modifican archivos en lugar
- Los comandos de linting solo reportan problemas
- Los análisis de seguridad no modifican código
- Todos los comandos Docker requieren que el servicio esté corriendo
- Los reportes JSON son útiles para integración con otras herramientas

---

**Última actualización**: Noviembre 2025
**Versión**: 1.0.0
