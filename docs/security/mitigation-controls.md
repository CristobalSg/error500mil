# 🛡️ Controles de Mitigación - OWASP A04 Insecure Design

Este documento detalla los controles de seguridad implementados y planificados para mitigar las amenazas identificadas en el Sistema de Gestión Horaria (SGH).

---

## 📊 Resumen Ejecutivo

| Categoría | Controles Implementados | En Progreso | Planificados | Total |
|-----------|------------------------|-------------|--------------|-------|
| Preventivos | 42 | 8 | 15 | 65 |
| Detectivos | 12 | 5 | 8 | 25 |
| Correctivos | 6 | 3 | 6 | 15 |
| **TOTAL** | **60** | **16** | **29** | **105** |

**Cobertura actual**: 57% (60/105 controles implementados)

---

## 🔐 1. Controles de Autenticación

### 1.1 Controles Preventivos

| ID | Control | Tipo | Estado | Amenaza Mitigada | Ubicación |
|----|---------|------|--------|------------------|-----------|
| AUTH-P-001 | JWT con algoritmo asimétrico (RS256) | Preventivo | ✅ | S2 (JWT forgery) | `infrastructure/auth.py` |
| AUTH-P-002 | Contraseñas hasheadas con bcrypt | Preventivo | ✅ | S1 (Credential theft) | `infrastructure/auth.py` |
| AUTH-P-003 | Salt único por contraseña | Preventivo | ✅ | S1 (Rainbow tables) | bcrypt automático |
| AUTH-P-004 | Tokens con expiración corta (30 min) | Preventivo | ✅ | S1, S2 (Token theft) | `config.py` |
| AUTH-P-005 | Refresh tokens con expiración (7 días) | Preventivo | ✅ | S1, S2 | `config.py` |
| AUTH-P-006 | Rate limiting en /login (5 req/min) | Preventivo | ✅ | S1 (Brute force) | `middlewares/rate_limit_middleware.py` |
| AUTH-P-007 | Account lockout tras intentos fallidos | Preventivo | ⏳ | S1 (Brute force) | Planificado v2.0 |
| AUTH-P-008 | MFA para administradores | Preventivo | ⏳ | S1 (Suplantación) | Planificado v2.0 |
| AUTH-P-009 | Token binding a IP/dispositivo | Preventivo | ⏳ | S2 (Token replay) | Planificado |
| AUTH-P-010 | Política de contraseñas robusta | Preventivo | ✅ | S1 (Weak passwords) | Validación Pydantic |

**Efectividad**: 🟢 70% implementada

**Gaps Críticos**:
- ⏳ Account lockout (Alta prioridad)
- ⏳ MFA para administradores (Media prioridad)

---

### 1.2 Controles Detectivos

| ID | Control | Tipo | Estado | Detección | Ubicación |
|----|---------|------|--------|-----------|-----------|
| AUTH-D-001 | Logging de intentos de login | Detectivo | ✅ | S1 (Brute force) | `middlewares/security_logging_middleware.py` |
| AUTH-D-002 | Logging de logins exitosos | Detectivo | ✅ | S1 (Acceso no autorizado) | Middleware |
| AUTH-D-003 | Alertas de login desde nueva IP | Detectivo | ⏳ | S1 (Compromiso) | Planificado |
| AUTH-D-004 | Detección de patrones de ataque | Detectivo | ⏳ | S1, D1 (Ataques automatizados) | Planificado con WAF |
| AUTH-D-005 | Monitoreo de tokens expirados | Detectivo | 🔄 | S2 (Token abuse) | En desarrollo |

**Efectividad**: 🟡 40% implementada

---

### 1.3 Controles Correctivos

| ID | Control | Tipo | Estado | Respuesta | Proceso |
|----|---------|------|--------|-----------|---------|
| AUTH-C-001 | Invalidación manual de tokens | Correctivo | 🔄 | S1, S2 (Compromiso) | Blacklist en desarrollo |
| AUTH-C-002 | Reset de contraseña forzado | Correctivo | ⏳ | S1 (Compromiso) | Planificado |
| AUTH-C-003 | Revocación de todos los tokens de usuario | Correctivo | ⏳ | S1 (Compromiso masivo) | Planificado |

**Efectividad**: 🔴 0% implementada (Alta prioridad)

---

## 🔒 2. Controles de Autorización (RBAC)

### 2.1 Controles Preventivos

| ID | Control | Tipo | Estado | Amenaza Mitigada | Ubicación |
|----|---------|------|--------|------------------|-----------|
| AUTHZ-P-001 | RBAC granular con permisos | Preventivo | ✅ | E1, E2 (Escalación) | `domain/authorization.py` |
| AUTHZ-P-002 | Verificación de permisos en dependencies | Preventivo | ✅ | E1, E2, E3 | `infrastructure/dependencies.py` |
| AUTHZ-P-003 | Verificación de propiedad de recursos | Preventivo | ✅ | E1 (Acceso horizontal) | `application/services/authorization_service.py` |
| AUTHZ-P-004 | Usuarios no pueden cambiar su propio rol | Preventivo | ✅ | E2 (Escalación vertical) | `use_cases/user_management_use_cases.py` |
| AUTHZ-P-005 | Principio de menor privilegio aplicado | Preventivo | ✅ | E2, E4 (Privilege creep) | Diseño RBAC |
| AUTHZ-P-006 | Separación de responsabilidades | Preventivo | ✅ | E2 (Conflictos de interés) | Roles mutuamente exclusivos |
| AUTHZ-P-007 | Mediación completa (todas requests verificadas) | Preventivo | ✅ | E3 (Bypass) | Dependencies obligatorias |
| AUTHZ-P-008 | Validación de estado del usuario (activo) | Preventivo | ✅ | S1, E1 (Cuentas deshabilitadas) | Auth use cases |

**Efectividad**: 🟢 100% implementada

**Fortalezas**:
- Sistema RBAC robusto y bien documentado
- Verificación en múltiples capas
- Tests exhaustivos

---

### 2.2 Controles Detectivos

| ID | Control | Tipo | Estado | Detección | Ubicación |
|----|---------|------|--------|-----------|-----------|
| AUTHZ-D-001 | Logging de accesos denegados (403) | Detectivo | ✅ | E1, E2, E3 (Intentos de escalación) | `middlewares/security_logging_middleware.py` |
| AUTHZ-D-002 | Auditoría de cambios de permisos | Detectivo | 🔄 | E2, E4 (Privilege creep) | En desarrollo |
| AUTHZ-D-003 | Análisis de patrones de acceso | Detectivo | ⏳ | E1 (Accesos anómalos) | Planificado con ML |
| AUTHZ-D-004 | Alertas de cambios de rol | Detectivo | ⏳ | E2 (Escalación vertical) | Planificado |

**Efectividad**: 🟡 25% implementada

---

### 2.3 Controles Correctivos

| ID | Control | Tipo | Estado | Respuesta | Proceso |
|----|---------|------|--------|-----------|---------|
| AUTHZ-C-001 | Reversión de cambios de permisos | Correctivo | ⏳ | E2 (Escalación) | Requiere auditoría completa |
| AUTHZ-C-002 | Deshabilitar cuenta comprometida | Correctivo | ✅ | E1, E2 (Acceso no autorizado) | API admin |
| AUTHZ-C-003 | Revisión periódica de permisos | Correctivo | ⏳ | E4 (Privilege creep) | Proceso manual trimestral |

**Efectividad**: 🟡 33% implementada

---

## 🛡️ 3. Controles de Validación y Sanitización

### 3.1 Controles Preventivos

| ID | Control | Tipo | Estado | Amenaza Mitigada | Ubicación |
|----|---------|------|--------|------------------|-----------|
| VAL-P-001 | Validación de entrada con Pydantic | Preventivo | ✅ | T1, T3 (Manipulation) | `domain/schemas.py` |
| VAL-P-002 | Sanitización de HTML/Scripts | Preventivo | ✅ | I1 (XSS), T1 | `middlewares/sanitization_middleware.py` |
| VAL-P-003 | ORM con prepared statements | Preventivo | ✅ | T2 (SQL Injection) | SQLAlchemy |
| VAL-P-004 | Validación de tipos de datos | Preventivo | ✅ | T1, T3 | Pydantic + Type hints |
| VAL-P-005 | Lista blanca de valores (enums) | Preventivo | ✅ | T1, T3 | `domain/entities.py` |
| VAL-P-006 | Validación de longitud de strings | Preventivo | ✅ | D3 (Resource exhaustion) | Pydantic constraints |
| VAL-P-007 | Validación de rangos numéricos | Preventivo | ✅ | T3 (Logic abuse) | Pydantic validators |
| VAL-P-008 | Validación de formatos (email, URL) | Preventivo | ✅ | T1 (Malformed data) | EmailStr, HttpUrl |
| VAL-P-009 | Rechazo automático de entrada inválida | Preventivo | ✅ | T1 (Bad input) | FastAPI 422 |

**Efectividad**: 🟢 100% implementada

**Fortalezas**:
- Validación robusta en múltiples capas
- Uso apropiado de Pydantic
- ORM previene inyecciones

---

### 3.2 Controles Detectivos

| ID | Control | Tipo | Estado | Detección | Ubicación |
|----|---------|------|--------|-----------|-----------|
| VAL-D-001 | Logging de inputs rechazados | Detectivo | ✅ | T1 (Ataques de inyección) | Logging automático |
| VAL-D-002 | Monitoreo de errores de validación | Detectivo | 🔄 | T1, T3 (Ataques) | En desarrollo con métricas |
| VAL-D-003 | Análisis de patrones de input malicioso | Detectivo | ⏳ | T1 (Ataques sofisticados) | Planificado con WAF |

**Efectividad**: 🟡 33% implementada

---

## 🔐 4. Controles de Protección de Datos

### 4.1 Controles Preventivos

| ID | Control | Tipo | Estado | Amenaza Mitigada | Ubicación |
|----|---------|------|--------|------------------|-----------|
| DATA-P-001 | HTTPS/TLS obligatorio | Preventivo | ✅ | S3 (MitM), I1 | Nginx/Ingress |
| DATA-P-002 | Headers de seguridad (HSTS, CSP) | Preventivo | ✅ | S3, I1 (XSS) | `main.py` |
| DATA-P-003 | Secretos en variables de entorno | Preventivo | ✅ | I1 (Info disclosure) | `config.py` |
| DATA-P-004 | No hardcodear secretos | Preventivo | ✅ | I1 (Leak de credenciales) | Code review process |
| DATA-P-005 | Contraseñas nunca en logs | Preventivo | ✅ | I1 (Log leaks) | `middlewares/security_logging_middleware.py` |
| DATA-P-006 | Tokens nunca en URLs | Preventivo | ✅ | I1 (Referrer leaks) | Header Authorization only |
| DATA-P-007 | Encriptación en tránsito | Preventivo | ✅ | I1 (MitM) | HTTPS |
| DATA-P-008 | Encriptación en reposo (BD) | Preventivo | 🔍 | I1 (DB dump) | Depende de infraestructura |
| DATA-P-009 | Stack traces solo en desarrollo | Preventivo | ✅ | I2 (Info disclosure) | Environment-based |
| DATA-P-010 | Mensajes de error genéricos | Preventivo | ✅ | I2 (System info) | Exception handlers |

**Efectividad**: 🟢 90% implementada

---

### 4.2 Controles Detectivos

| ID | Control | Tipo | Estado | Detección | Ubicación |
|----|---------|------|--------|-----------|-----------|
| DATA-D-001 | Detección de datos sensibles en logs | Detectivo | ⏳ | I1 (Leaks) | DLP tool planificado |
| DATA-D-002 | Monitoreo de accesos a datos sensibles | Detectivo | 🔄 | I5 (Mass data access) | En desarrollo |
| DATA-D-003 | Alertas de exportación masiva | Detectivo | ⏳ | I5 (Scraping) | Planificado |
| DATA-D-004 | Auditoría de cambios en datos críticos | Detectivo | 🔄 | T2 (Tampering) | Triggers en desarrollo |

**Efectividad**: 🔴 0% implementada

---

### 4.3 Controles Correctivos

| ID | Control | Tipo | Estado | Respuesta | Proceso |
|----|---------|------|--------|-----------|---------|
| DATA-C-001 | Backups automatizados | Correctivo | 🔍 | T2 (Data loss) | Requiere verificación infra |
| DATA-C-002 | Procedimiento de restauración | Correctivo | ⏳ | T2, D1 (Data loss) | DR plan en desarrollo |
| DATA-C-003 | Rotación de secretos comprometidos | Correctivo | ⏳ | I1 (Leak de secrets) | Proceso manual |

**Efectividad**: 🔴 0% implementada (Alta prioridad)

---

## 🚫 5. Controles de Denegación de Servicio (DoS)

### 5.1 Controles Preventivos

| ID | Control | Tipo | Estado | Amenaza Mitigada | Ubicación |
|----|---------|------|--------|------------------|-----------|
| DOS-P-001 | Rate limiting global | Preventivo | ✅ | D1 (Request flooding) | `middlewares/rate_limit_middleware.py` |
| DOS-P-002 | Rate limiting por usuario | Preventivo | ✅ | D1, D3 (Abuse) | Middleware |
| DOS-P-003 | Rate limiting por IP | Preventivo | ⏳ | D1 (DDoS) | Planificado |
| DOS-P-004 | Timeouts de requests | Preventivo | ✅ | D2 (Resource exhaustion) | Uvicorn config |
| DOS-P-005 | Paginación obligatoria | Preventivo | ✅ | D2 (Large queries) | Controllers |
| DOS-P-006 | Límite de tamaño de request | Preventivo | ✅ | D3 (Large payloads) | Nginx config |
| DOS-P-007 | Índices en BD | Preventivo | ✅ | D2 (Slow queries) | Database models |
| DOS-P-008 | Connection pooling | Preventivo | ✅ | D2 (Connection exhaustion) | SQLAlchemy |
| DOS-P-009 | Límites de cantidad de entidades | Preventivo | ⏳ | D3 (Logic abuse) | Planificado |
| DOS-P-010 | WAF | Preventivo | ⏳ | D1 (Application-layer attacks) | Planificado |

**Efectividad**: 🟡 60% implementada

---

### 5.2 Controles Detectivos

| ID | Control | Tipo | Estado | Detección | Ubicación |
|----|---------|------|--------|-----------|-----------|
| DOS-D-001 | Monitoreo de tasas de request | Detectivo | ⏳ | D1 (DDoS) | Prometheus planificado |
| DOS-D-002 | Alertas de uso de recursos | Detectivo | ⏳ | D2 (Resource exhaustion) | Monitoring planificado |
| DOS-D-003 | Detección de patrones de abuso | Detectivo | ⏳ | D3 (Logic abuse) | ML planificado |

**Efectividad**: 🔴 0% implementada

---

### 5.3 Controles Correctivos

| ID | Control | Tipo | Estado | Respuesta | Proceso |
|----|---------|------|--------|-----------|---------|
| DOS-C-001 | Escalado automático | Correctivo | 🔍 | D1, D2 (Alta carga) | Kubernetes HPA |
| DOS-C-002 | Blacklist de IPs maliciosas | Correctivo | ⏳ | D1 (DDoS) | Planificado |
| DOS-C-003 | Circuit breaker para servicios | Correctivo | ⏳ | D2 (Cascading failures) | Planificado |

**Efectividad**: 🔴 0% implementada

---

## 📝 6. Controles de Auditoría y No Repudio

### 6.1 Controles Preventivos

| ID | Control | Tipo | Estado | Amenaza Mitigada | Ubicación |
|----|---------|------|--------|------------------|-----------|
| AUDIT-P-001 | Logging estructurado | Preventivo | ✅ | R1 (Repudiation) | `application/logging_config.py` |
| AUDIT-P-002 | Timestamps en todos los logs | Preventivo | ✅ | R1 | Logging automático |
| AUDIT-P-003 | User ID en logs de acciones | Preventivo | ✅ | R1 | Middleware |
| AUDIT-P-004 | Logs inmutables (write-only) | Preventivo | ⏳ | R2 (Log tampering) | Sistema externo planificado |
| AUDIT-P-005 | Tabla de auditoría para cambios críticos | Preventivo | 🔄 | R1, T2 | En desarrollo |

**Efectividad**: 🟡 60% implementada

---

### 6.2 Controles Detectivos

| ID | Control | Tipo | Estado | Detección | Ubicación |
|----|---------|------|--------|-----------|-----------|
| AUDIT-D-001 | Monitoreo de integridad de logs | Detectivo | ⏳ | R2 (Tampering) | Checksums planificados |
| AUDIT-D-002 | Alertas de acciones sospechosas | Detectivo | ⏳ | T2, T3 (Abuse) | SIEM planificado |
| AUDIT-D-003 | Análisis de auditoría periódico | Detectivo | ⏳ | Todas (Revisión) | Proceso manual planificado |

**Efectividad**: 🔴 0% implementada

---

### 6.3 Controles Correctivos

| ID | Control | Tipo | Estado | Respuesta | Proceso |
|----|---------|------|--------|-----------|---------|
| AUDIT-C-001 | Investigación de eventos | Correctivo | ⏳ | Todas (Incident response) | IR plan en desarrollo |
| AUDIT-C-002 | Restauración de datos auditados | Correctivo | ⏳ | T2 (Tampering) | Requiere auditoría completa |

**Efectividad**: 🔴 0% implementada

---

## 📊 Matriz de Cobertura por Amenaza

| Amenaza | Preventivos | Detectivos | Correctivos | Cobertura Total |
|---------|-------------|------------|-------------|-----------------|
| S1 (Spoofing - Credential) | 🟢 70% | 🟡 40% | 🔴 0% | 🟡 37% |
| S2 (Spoofing - JWT) | 🟢 80% | 🟡 40% | 🔴 0% | 🟡 40% |
| S3 (Spoofing - MitM) | 🟢 100% | N/A | N/A | 🟢 100% |
| T1 (Tampering - Transit) | 🟢 100% | 🟡 33% | N/A | 🟢 67% |
| T2 (Tampering - Database) | 🟢 90% | 🔴 0% | 🔴 0% | 🟡 30% |
| T3 (Tampering - Logic) | 🟡 60% | 🟡 33% | 🔴 0% | 🟡 31% |
| R1 (Repudiation - Actions) | 🟡 60% | 🔴 0% | 🔴 0% | 🔴 20% |
| R2 (Repudiation - Logs) | 🟡 40% | 🔴 0% | N/A | 🔴 13% |
| I1 (Info Disclosure - Logs) | 🟢 90% | 🔴 0% | N/A | 🟡 30% |
| I2 (Info Disclosure - Errors) | 🟢 100% | N/A | N/A | 🟢 100% |
| I3 (Enumeration) | 🟡 60% | N/A | N/A | 🟡 60% |
| I4 (Predictable IDs) | 🟡 50% | N/A | N/A | 🟡 50% |
| I5 (API Disclosure) | 🟢 90% | 🔴 0% | N/A | 🟡 30% |
| D1 (DoS - Rate) | 🟡 60% | 🔴 0% | 🔴 0% | 🔴 20% |
| D2 (DoS - Resources) | 🟢 80% | 🔴 0% | 🔴 0% | 🔴 27% |
| D3 (DoS - Logic) | 🟡 40% | 🔴 0% | 🔴 0% | 🔴 13% |
| E1 (Escalation - Horizontal) | 🟢 100% | 🟡 25% | 🟡 33% | 🟢 53% |
| E2 (Escalation - Vertical) | 🟢 100% | 🟡 25% | 🟡 33% | 🟢 53% |
| E3 (Auth Bypass) | 🟢 100% | 🟡 25% | 🟡 33% | 🟢 53% |
| E4 (Privilege Creep) | 🟢 100% | 🟡 25% | 🟡 33% | 🟢 53% |

### Análisis de Gaps

**Gaps Críticos (Alta Prioridad)**:
1. 🔴 **Controles Correctivos**: Solo 33% de cobertura
2. 🔴 **Controles Detectivos para DoS**: 0% de cobertura
3. 🔴 **Auditoría y No Repudio**: 13-20% de cobertura
4. 🔴 **Protección de Datos - Detectivos**: 0% de cobertura

**Fortalezas**:
1. 🟢 **RBAC y Autorización**: 100% de controles preventivos
2. 🟢 **Validación de Entrada**: 100% de controles preventivos
3. 🟢 **Protección básica de datos**: 90% de controles preventivos

---

## 🎯 Plan de Acción Priorizado

### Fase 1: Inmediato (1-2 semanas)

| Prioridad | Control | Esfuerzo | Impacto |
|-----------|---------|----------|---------|
| 🔴 CRÍTICO | AUTH-P-007: Account lockout | Bajo | Alto |
| 🔴 CRÍTICO | DOS-P-009: Límite de restricciones (50 por docente) | Bajo | Medio |
| 🔴 CRÍTICO | AUDIT-P-005: Tabla de auditoría | Medio | Alto |
| 🟠 ALTO | DATA-C-001: Verificar backups | Bajo | Alto |

### Fase 2: Corto Plazo (1 mes)

| Prioridad | Control | Esfuerzo | Impacto |
|-----------|---------|----------|---------|
| 🟠 ALTO | AUTH-C-001: Token blacklist (Redis) | Medio | Alto |
| 🟠 ALTO | DOS-P-003: Rate limiting por IP | Medio | Medio |
| 🟠 ALTO | AUTH-D-003: Alertas de login desde nueva IP | Medio | Medio |
| 🟠 ALTO | DATA-D-002: Monitoreo de accesos masivos | Medio | Medio |
| 🟡 MEDIO | AUTHZ-D-002: Auditoría de cambios de permisos | Medio | Medio |

### Fase 3: Mediano Plazo (3 meses)

| Prioridad | Control | Esfuerzo | Impacto |
|-----------|---------|----------|---------|
| 🟠 ALTO | AUTH-P-008: MFA para administradores | Alto | Alto |
| 🟡 MEDIO | AUDIT-P-004: Logs en sistema externo (ELK) | Alto | Alto |
| 🟡 MEDIO | DOS-D-001: Monitoreo con Prometheus | Alto | Medio |
| 🟡 MEDIO | DATA-C-002: Plan de DR completo | Alto | Alto |
| 🟡 MEDIO | DOS-P-010: WAF | Alto | Alto |

### Fase 4: Largo Plazo (6+ meses)

| Prioridad | Control | Esfuerzo | Impacto |
|-----------|---------|----------|---------|
| 🟡 MEDIO | AUTHZ-D-003: Análisis con ML | Muy Alto | Medio |
| 🟢 BAJO | DOS-P-010: DDoS protection (CDN) | Alto | Medio |
| 🟢 BAJO | AUDIT-D-002: SIEM completo | Muy Alto | Alto |

---

## 📈 Métricas de Efectividad

### KPIs de Seguridad

| Métrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| % Controles Implementados | 80% | 57% | 🟡 |
| % Controles Preventivos | 90% | 65% | 🟡 |
| % Controles Detectivos | 60% | 33% | 🔴 |
| % Controles Correctivos | 70% | 40% | 🔴 |
| Amenazas con >70% cobertura | 80% | 45% | 🔴 |
| Tests de seguridad passing | 100% | 100% | 🟢 |
| Incidentes de seguridad | 0 | 0 | 🟢 |

### Tendencias (Proyección)

```
Cobertura de Controles:
                                           ┌─ Goal: 80%
57% ──●                                    │
      │ \                                  │
      │  \                                 │
      │   ●── 65% (Fase 1)                │
      │    \                               │
      │     \                              │
      │      ●── 73% (Fase 2)             │
      │       \                            │
      │        ●─── 78% (Fase 3)          │
      │         \                          │
      │          ●──── 82% (Fase 4)       ●
      └─────────────────────────────────────────
       Now    1m     3m      6m     12m
```

---

## 🔄 Proceso de Revisión

### Frecuencia de Revisión

- **Semanal**: Verificar controles críticos (AUTH, AUTHZ)
- **Mensual**: Revisar implementación de controles planificados
- **Trimestral**: Auditoría completa de efectividad
- **Anual**: Revisión estratégica completa

### Checklist de Revisión

- [ ] ¿Se implementaron todos los controles planificados?
- [ ] ¿Los controles existentes siguen siendo efectivos?
- [ ] ¿Hay nuevas amenazas no cubiertas?
- [ ] ¿Los KPIs de seguridad se cumplen?
- [ ] ¿Hay incidentes que requieran nuevos controles?

---

## 📚 Referencias

- [OWASP ASVS 4.0](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls v8](https://www.cisecurity.org/controls/)

---

**Última actualización**: 11 de noviembre de 2025  
**Próxima revisión**: Diciembre 2025  
**Responsable**: Equipo de Desarrollo SGH
