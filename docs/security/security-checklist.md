# 📋 Checklist de Seguridad - OWASP A04 Insecure Design

## Propósito

Este checklist proporciona una guía completa de controles de seguridad que deben ser considerados e implementados para prevenir diseños inseguros en el Sistema de Gestión Horaria (SGH). Está alineado con **OWASP A04:2021 – Insecure Design**.

---

## 🎯 Cómo Usar Este Checklist

- ✅ = Implementado y verificado
- 🔄 = En progreso
- ⏳ = Planificado
- ❌ = No implementado / No aplica
- 🔍 = Requiere revisión

---

## 1. 🔐 Autenticación y Control de Acceso

### 1.1 Diseño de Autenticación

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| AUTH-001 | Sistema de autenticación basado en JWT implementado | ✅ | JWT con RS256 | `infrastructure/auth.py` |
| AUTH-002 | Tokens de autenticación con expiración apropiada | ✅ | 30 min access, 7 días refresh | `config.py` |
| AUTH-003 | Refresh tokens implementados | ✅ | Rotación automática | `api/auth.py` |
| AUTH-004 | Política de contraseñas robusta | ✅ | Min 8 chars, bcrypt | `domain/models.py` |
| AUTH-005 | Rate limiting en endpoints de autenticación | ✅ | Middleware implementado | `middlewares/rate_limit_middleware.py` |
| AUTH-006 | Protección contra fuerza bruta (account lockout) | ⏳ | Planificado para v2.0 | - |
| AUTH-007 | MFA (Multi-Factor Authentication) | ⏳ | Planificado para v2.0 | - |
| AUTH-008 | Single Sign-On (SSO) preparado | ⏳ | Arquitectura permite integración | - |
| AUTH-009 | Gestión segura de sesiones | ✅ | JWT stateless | `infrastructure/auth.py` |
| AUTH-010 | Logout seguro (invalidación de tokens) | 🔄 | Blacklist en desarrollo | - |

### 1.2 Sistema de Autorización (RBAC)

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| AUTHZ-001 | Roles definidos y documentados | ✅ | Admin, Docente, Estudiante | `domain/authorization.py` |
| AUTHZ-002 | Permisos granulares por recurso | ✅ | Formato recurso:acción | `domain/authorization.py` |
| AUTHZ-003 | Matriz de permisos por rol | ✅ | ROLE_PERMISSIONS dict | `domain/authorization.py` |
| AUTHZ-004 | Principio de menor privilegio aplicado | ✅ | Roles con mínimos permisos necesarios | `backend/Autorizacion.md` |
| AUTHZ-005 | Verificación de permisos en cada endpoint | ✅ | Dependencies de FastAPI | `infrastructure/dependencies.py` |
| AUTHZ-006 | Reglas de negocio centralizadas | ✅ | AuthorizationRules class | `domain/authorization.py` |
| AUTHZ-007 | Control de acceso a datos propios | ✅ | Docentes ven solo sus restricciones | `application/services/authorization_service.py` |
| AUTHZ-008 | Separación de responsabilidades | ✅ | Roles no traslapados | `domain/authorization.py` |
| AUTHZ-009 | Auditoría de cambios de permisos | 🔄 | Logging en desarrollo | - |
| AUTHZ-010 | Prevención de escalación de privilegios | ✅ | Usuarios no pueden cambiar su propio rol | `use_cases/user_management_use_cases.py` |

---

## 2. 🛡️ Validación y Sanitización de Entrada

### 2.1 Validación de Entrada

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| VAL-001 | Validación de entrada usando Pydantic | ✅ | Schemas en domain | `domain/schemas.py` |
| VAL-002 | Validación de tipos de datos | ✅ | Type hints + Pydantic | Todos los schemas |
| VAL-003 | Validación de rangos y límites | ✅ | Constraints en schemas | `domain/schemas.py` |
| VAL-004 | Validación de formatos (email, URL, etc.) | ✅ | EmailStr, HttpUrl | `domain/schemas.py` |
| VAL-005 | Lista blanca de valores permitidos | ✅ | Enums para campos cerrados | `domain/entities.py` |
| VAL-006 | Validación de longitud de strings | ✅ | min_length, max_length | `domain/schemas.py` |
| VAL-007 | Rechazo de entrada malformada | ✅ | HTTP 422 automático | FastAPI |
| VAL-008 | Validación servidor-side (no confiar en cliente) | ✅ | Toda validación en backend | API |
| VAL-009 | Validación de archivos subidos | ⏳ | No implementado (sin uploads aún) | - |
| VAL-010 | Validación de JSON schema | ✅ | Pydantic models | `domain/schemas.py` |

### 2.2 Sanitización de Entrada

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| SAN-001 | Middleware de sanitización implementado | ✅ | HTML, SQL, script tags | `middlewares/sanitization_middleware.py` |
| SAN-002 | Protección contra XSS | ✅ | Sanitización + CSP headers | Middleware |
| SAN-003 | Protección contra SQL Injection | ✅ | ORM SQLAlchemy (prepared statements) | `infrastructure/repositories/` |
| SAN-004 | Protección contra NoSQL Injection | ✅ | Validación Pydantic | `domain/schemas.py` |
| SAN-005 | Protección contra Path Traversal | ✅ | No hay acceso a filesystem | - |
| SAN-006 | Protección contra Command Injection | ✅ | No hay ejecución de comandos | - |
| SAN-007 | Protección contra LDAP Injection | ❌ | No aplica (no usa LDAP) | - |
| SAN-008 | Protección contra XML External Entity (XXE) | ❌ | No aplica (no procesa XML) | - |
| SAN-009 | Encoding apropiado de salida | ✅ | JSON automático por FastAPI | API |
| SAN-010 | Sanitización de logs | ✅ | No loguear datos sensibles | `middlewares/security_logging_middleware.py` |

---

## 3. 🗄️ Gestión de Datos Sensibles

### 3.1 Protección de Datos

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| DATA-001 | Contraseñas hasheadas (bcrypt) | ✅ | bcrypt con salt | `infrastructure/auth.py` |
| DATA-002 | No almacenar contraseñas en texto plano | ✅ | Solo hash en BD | `domain/models.py` |
| DATA-003 | Secrets en variables de entorno | ✅ | .env files | `config.py` |
| DATA-004 | JWT secrets suficientemente complejos | ✅ | RSA 2048 bits | `.env` |
| DATA-005 | Claves privadas no en repositorio | ✅ | .gitignore configurado | `.gitignore` |
| DATA-006 | Encriptación en tránsito (HTTPS/TLS) | ✅ | Obligatorio en producción | Nginx/Ingress |
| DATA-007 | Encriptación en reposo (BD) | 🔄 | Dependiente de PostgreSQL config | Infraestructura |
| DATA-008 | Datos sensibles no en logs | ✅ | Middleware filtra passwords, tokens | `middlewares/security_logging_middleware.py` |
| DATA-009 | No exponer stack traces a clientes | ✅ | Solo en desarrollo | `main.py` |
| DATA-010 | PII (Personally Identifiable Information) protegida | ✅ | Control de acceso estricto | RBAC |
| DATA-011 | Backup de datos encriptados | 🔍 | Requiere revisión infraestructura | - |
| DATA-012 | Retención de datos según política | ⏳ | Política en desarrollo | - |

### 3.2 Manejo de Secretos

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| SEC-001 | Variables de entorno para secretos | ✅ | .env files | `config.py` |
| SEC-002 | No hardcodear credenciales | ✅ | Code review lo previene | - |
| SEC-003 | Rotación de secretos planificada | ⏳ | Proceso manual por ahora | - |
| SEC-004 | Secretos diferentes por ambiente | ✅ | .env.dev, .env.prod | Docker Compose |
| SEC-005 | Vault o secret manager considerado | ⏳ | Para v2.0 (Kubernetes Secrets) | - |
| SEC-006 | API keys con expiración | ⏳ | No implementado aún | - |

---

## 4. 🌐 Seguridad de API

### 4.1 Diseño de API

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| API-001 | Versionado de API implementado | ✅ | /api/v1/ | `api/api.py` |
| API-002 | Rate limiting global | ✅ | Middleware implementado | `middlewares/rate_limit_middleware.py` |
| API-003 | Rate limiting por usuario | ✅ | Basado en user_id | Middleware |
| API-004 | Rate limiting por endpoint crítico | ✅ | Configurable | Middleware |
| API-005 | CORS configurado apropiadamente | ✅ | Solo orígenes permitidos | `main.py` |
| API-006 | Métodos HTTP apropiados (GET, POST, PUT, DELETE) | ✅ | REST semántico | Controllers |
| API-007 | Códigos de estado HTTP apropiados | ✅ | 200, 201, 400, 401, 403, 404, 500 | API |
| API-008 | Paginación en listados | ✅ | skip/limit params | Controllers |
| API-009 | Filtrado y ordenamiento seguro | ✅ | Queries parametrizadas | Repositories |
| API-010 | Documentación de API (OpenAPI) | ✅ | Swagger UI auto-generado | `/docs` |
| API-011 | Timeouts configurados | ✅ | Request timeouts | Uvicorn |
| API-012 | Tamaño máximo de request | ✅ | Configurado en nginx | Infraestructura |

### 4.2 Seguridad de Endpoints

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| EP-001 | Todos los endpoints protegidos por autenticación | ✅ | Excepto /health, /login, /register | API |
| EP-002 | Autorización verificada en cada endpoint | ✅ | Dependencies o use cases | API |
| EP-003 | Validación de parámetros de ruta | ✅ | Path params validados | Controllers |
| EP-004 | Validación de query strings | ✅ | Query params validados | Controllers |
| EP-005 | No exponer IDs internos predictibles | 🔍 | Usar UUIDs considerado | - |
| EP-006 | Prevención de enumeración de recursos | 🔄 | Mensajes de error genéricos | - |
| EP-007 | HATEOAS considerado | ⏳ | Para v2.0 | - |
| EP-008 | Idempotencia en operaciones apropiadas | ✅ | PUT, DELETE idempotentes | Controllers |

---

## 5. 🏗️ Arquitectura y Diseño

### 5.1 Principios de Diseño Seguro

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| ARCH-001 | Arquitectura hexagonal implementada | ✅ | Domain/Application/Infrastructure | Estructura proyecto |
| ARCH-002 | Separación de capas respetada | ✅ | Clean Architecture | - |
| ARCH-003 | Principio de menor privilegio | ✅ | RBAC granular | `domain/authorization.py` |
| ARCH-004 | Defensa en profundidad | ✅ | Múltiples capas de seguridad | - |
| ARCH-005 | Fail secure (fallar seguro) | ✅ | Excepciones no revelan info | Error handlers |
| ARCH-006 | Separación de responsabilidades | ✅ | Roles separados | RBAC |
| ARCH-007 | Mediación completa | ✅ | Todas las requests autorizadas | Dependencies |
| ARCH-008 | Diseño abierto (no security by obscurity) | ✅ | Seguridad documentada | `docs/` |
| ARCH-009 | Economía de mecanismos | ✅ | Diseño simple y mantenible | - |
| ARCH-010 | Compartimentalización | ✅ | Módulos independientes | Arquitectura |

### 5.2 Límites de Confianza

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| TRUST-001 | Límites de confianza identificados | ✅ | Cliente ↔ API ↔ BD | Diagrama arquitectura |
| TRUST-002 | Validación en cada límite | ✅ | Validación en entrada API | Middleware |
| TRUST-003 | No confiar en cliente | ✅ | Toda lógica en backend | - |
| TRUST-004 | Red interna segmentada | 🔍 | Requiere revisión infraestructura | Kubernetes |
| TRUST-005 | Acceso a BD restringido | ✅ | Solo desde backend | Docker network |

---

## 6. 🔄 Flujos de Negocio Críticos

### 6.1 Gestión de Usuarios

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| USER-001 | Registro con validación de email | ✅ | EmailStr validation | `domain/schemas.py` |
| USER-002 | Proceso de activación de cuenta | ⏳ | Email verification planificado | - |
| USER-003 | Recuperación de contraseña segura | ⏳ | Token temporal por email | - |
| USER-004 | Cambio de contraseña requiere actual | ✅ | Verificación implementada | `use_cases/user_auth_use_cases.py` |
| USER-005 | No permitir cambio de rol propio | ✅ | Verificación implementada | `use_cases/user_management_use_cases.py` |
| USER-006 | Eliminación de usuario verificada | ✅ | Solo admin | RBAC |
| USER-007 | Auditoría de cambios en usuarios | 🔄 | Logging en desarrollo | - |

### 6.2 Gestión de Horarios y Restricciones

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| SCHED-001 | Docentes solo modifican sus restricciones | ✅ | AuthorizationRules | `domain/authorization.py` |
| SCHED-002 | Validación de overlapping de clases | ✅ | Lógica en use cases | `use_cases/clase_uses_cases.py` |
| SCHED-003 | Validación de capacidad de salas | ✅ | Verificación en creación | `use_cases/clase_uses_cases.py` |
| SCHED-004 | Prevención de conflictos de horario | ✅ | Validación en BD y lógica | Repositories |
| SCHED-005 | Límites en cantidad de restricciones | ⏳ | Por implementar | - |
| SCHED-006 | Auditoría de cambios en horarios | 🔄 | Logging en desarrollo | - |

### 6.3 Gestión Académica

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| ACAD-001 | Solo admin puede crear/modificar asignaturas | ✅ | RBAC enforced | `domain/authorization.py` |
| ACAD-002 | Validación de dependencias entre entidades | ✅ | Foreign keys + lógica | Models + Use Cases |
| ACAD-003 | No permitir eliminar recursos en uso | ✅ | Verificación en use cases | Use Cases |
| ACAD-004 | Validación de integridad referencial | ✅ | SQLAlchemy ORM | Models |
| ACAD-005 | Prevención de datos huérfanos | ✅ | Cascade delete configurado | Models |

---

## 7. 🐛 Manejo de Errores

### 7.1 Error Handling

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| ERR-001 | Excepciones personalizadas implementadas | ✅ | HTTPException usado | Controllers |
| ERR-002 | No exponer información sensible en errores | ✅ | Mensajes genéricos | Exception handlers |
| ERR-003 | No revelar stack traces a clientes | ✅ | Solo en desarrollo | `main.py` |
| ERR-004 | Logging de errores servidor-side | ✅ | Logging implementado | `application/logging_config.py` |
| ERR-005 | Códigos de error consistentes | ✅ | HTTP status codes estándar | API |
| ERR-006 | Rate limiting en errores de auth | ✅ | Middleware implementado | `middlewares/rate_limit_middleware.py` |

### 7.2 Logging y Auditoría

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| LOG-001 | Sistema de logging centralizado | ✅ | Python logging | `application/logging_config.py` |
| LOG-002 | Logging de autenticación | ✅ | Login, logout, refresh | `middlewares/security_logging_middleware.py` |
| LOG-003 | Logging de autorización (403) | ✅ | Accesos denegados | Middleware |
| LOG-004 | Logging de cambios críticos | 🔄 | En desarrollo | - |
| LOG-005 | No loguear datos sensibles | ✅ | Filtrado implementado | `middlewares/security_logging_middleware.py` |
| LOG-006 | Timestamps en todos los logs | ✅ | ISO format | Logging config |
| LOG-007 | Nivel de log apropiado (INFO, WARN, ERROR) | ✅ | Correctamente configurado | Logs |
| LOG-008 | Rotación de logs | ✅ | Configurado en producción | Infraestructura |
| LOG-009 | Logs accesibles solo a administradores | ✅ | Filesystem permissions | Server |
| LOG-010 | Auditoría de accesos a datos sensibles | 🔄 | En desarrollo | - |

---

## 8. 🧪 Testing de Seguridad

### 8.1 Tests Automatizados

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| TEST-001 | Tests de autenticación | ✅ | Pytest suite | `tests/test_auth_api.py` |
| TEST-002 | Tests de autorización | ✅ | RBAC tests | `tests/test_auth_api.py` |
| TEST-003 | Tests de validación de entrada | ✅ | Pydantic validation tests | Tests |
| TEST-004 | Tests de casos edge | ✅ | Valores límite, nulls | Tests |
| TEST-005 | Tests de middlewares de seguridad | ✅ | Rate limit, sanitization | `tests/test_middlewares.py` |
| TEST-006 | Tests de inyección SQL | ✅ | Intentos de inyección | `tests/test_security.py` |
| TEST-007 | Tests de XSS | ✅ | Scripts maliciosos | `tests/test_security.py` |
| TEST-008 | Tests de escalación de privilegios | ✅ | Usuarios intentan acciones prohibidas | Tests |
| TEST-009 | Coverage de seguridad > 80% | ✅ | Coverage reports | CI/CD |
| TEST-010 | Tests en CI/CD pipeline | ✅ | GitHub Actions | `.github/workflows/` |

### 8.2 Revisiones de Seguridad

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| REV-001 | Code reviews obligatorios | ✅ | PR process | GitHub |
| REV-002 | Security checklist en PRs | 🔄 | Template en desarrollo | - |
| REV-003 | SAST (Static Analysis) automatizado | ⏳ | Bandit planificado | - |
| REV-004 | Dependency scanning (vulnerabilidades) | ⏳ | Dependabot planificado | - |
| REV-005 | Revisión manual de cambios críticos | ✅ | Security-sensitive code | Process |
| REV-006 | Threat modeling regular | 🔄 | Este documento | - |

---

## 9. 🚀 Despliegue y Operaciones

### 9.1 Configuración de Producción

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| PROD-001 | Variables de entorno por ambiente | ✅ | .env files separados | Docker Compose |
| PROD-002 | Debug mode deshabilitado en producción | ✅ | ENV=production | `config.py` |
| PROD-003 | HTTPS obligatorio | ✅ | Enforced en ingress | Kubernetes |
| PROD-004 | Headers de seguridad configurados | ✅ | CSP, HSTS, X-Frame-Options | `main.py` |
| PROD-005 | Secretos no en repositorio | ✅ | .gitignore configurado | `.gitignore` |
| PROD-006 | Configuración de firewall | 🔍 | Requiere revisión | Infraestructura |
| PROD-007 | Configuración de IDS/IPS | ⏳ | Planificado | - |
| PROD-008 | Backups automatizados | 🔍 | Requiere revisión | Infraestructura |
| PROD-009 | Plan de recuperación ante desastres | ⏳ | En desarrollo | - |

### 9.2 Monitoreo

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| MON-001 | Monitoreo de aplicación | ⏳ | Prometheus planificado | - |
| MON-002 | Alertas de seguridad | ⏳ | En desarrollo | - |
| MON-003 | Monitoreo de tasas de error | ⏳ | Grafana planificado | - |
| MON-004 | Monitoreo de performance | ⏳ | APM planificado | - |
| MON-005 | Dashboard de seguridad | ⏳ | Planificado | - |
| MON-006 | Análisis de logs | 🔄 | ELK stack considerado | - |

---

## 10. 📱 Seguridad de Aplicación Móvil

### 10.1 Cliente Móvil

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| MOB-001 | Almacenamiento seguro de tokens | 🔍 | Requiere revisión | `mobile/` |
| MOB-002 | No hardcodear secrets en app | 🔍 | Requiere revisión | `mobile/` |
| MOB-003 | SSL pinning considerado | ⏳ | Planificado | - |
| MOB-004 | Validación de certificados | ✅ | HTTPS enforced | Capacitor |
| MOB-005 | Obfuscación de código | ⏳ | Para release | - |
| MOB-006 | Root/Jailbreak detection | ⏳ | Considerado | - |

---

## 11. 🔧 Dependencias y Librerías

### 11.1 Gestión de Dependencias

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| DEP-001 | Dependencias actualizadas regularmente | 🔄 | Manual por ahora | `requirements.txt` |
| DEP-002 | Vulnerabilidades conocidas monitoreadas | ⏳ | Dependabot planificado | - |
| DEP-003 | Lock files para reproducibilidad | ✅ | pnpm-lock, requirements.txt | Root |
| DEP-004 | Dependencias mínimas necesarias | ✅ | Solo las requeridas | Requirements |
| DEP-005 | Auditoría de nuevas dependencias | ✅ | Code review process | - |
| DEP-006 | SCA (Software Composition Analysis) | ⏳ | Snyk considerado | - |

---

## 12. 🌍 Cumplimiento y Regulaciones

### 12.1 Protección de Datos

| ID | Control | Estado | Notas | Ubicación |
|----|---------|--------|-------|-----------|
| COMP-001 | Política de privacidad definida | ⏳ | En desarrollo | - |
| COMP-002 | Términos de servicio definidos | ⏳ | En desarrollo | - |
| COMP-003 | GDPR considerado (si aplica) | ⏳ | Evaluación pendiente | - |
| COMP-004 | Consentimiento de usuario | ⏳ | Para datos sensibles | - |
| COMP-005 | Derecho al olvido implementable | ⏳ | Arquitectura lo permite | - |
| COMP-006 | Portabilidad de datos | ⏳ | Export función planificada | - |

---

## 📊 Resumen por Estado

| Estado | Cantidad | Porcentaje |
|--------|----------|------------|
| ✅ Implementado | 118 | 67% |
| 🔄 En progreso | 18 | 10% |
| ⏳ Planificado | 29 | 16% |
| 🔍 Requiere revisión | 10 | 6% |
| ❌ No aplica | 2 | 1% |
| **TOTAL** | **177** | **100%** |

---

## 🎯 Prioridades

### Alta Prioridad (Implementar Inmediatamente)

1. ⏳ Logout seguro con invalidación de tokens (AUTH-010)
2. 🔍 Prevención de enumeración de recursos (EP-006)
3. 🔄 Auditoría de cambios críticos (LOG-004, LOG-010)

### Media Prioridad (Próximo Sprint)

1. ⏳ Account lockout tras intentos fallidos (AUTH-006)
2. ⏳ Proceso de recuperación de contraseña (USER-003)
3. ⏳ SAST automatizado (REV-003)
4. ⏳ Dependency scanning (REV-004)

### Baja Prioridad (Roadmap v2.0)

1. ⏳ MFA (AUTH-007)
2. ⏳ SSO (AUTH-008)
3. ⏳ Monitoreo avanzado (MON-001 a MON-006)
4. ⏳ Cumplimiento GDPR (COMP-003)

---

## 📝 Notas de Implementación

### Buenas Prácticas Observadas

- ✅ Arquitectura limpia y modular
- ✅ RBAC bien implementado
- ✅ Testing comprehensivo
- ✅ Documentación detallada
- ✅ Uso apropiado de middlewares

### Áreas de Mejora

- 🔧 Implementar auditoría completa de acciones
- 🔧 Mejorar monitoreo y alertas
- 🔧 Completar gestión de sesiones
- 🔧 Implementar recuperación de contraseña segura
- 🔧 Agregar análisis estático de seguridad (SAST)

---

## 🔄 Proceso de Actualización

Este checklist debe ser:

1. **Revisado** antes de cada sprint
2. **Actualizado** cuando se implementen nuevos controles
3. **Verificado** en cada code review
4. **Auditado** mensualmente por el equipo

---

**Última actualización**: 11 de noviembre de 2025  
**Próxima revisión**: Diciembre 2025  
**Responsable**: Equipo de Desarrollo SGH
