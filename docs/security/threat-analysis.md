# 🔍 Análisis de Amenazas - OWASP A04 Insecure Design

## Metodología: STRIDE

Este documento utiliza la metodología **STRIDE** de Microsoft para identificar y analizar amenazas en el Sistema de Gestión Horaria (SGH).

### ¿Qué es STRIDE?

STRIDE es un acrónimo que representa seis categorías de amenazas:

| Categoría | Descripción | Propiedad de Seguridad Violada |
|-----------|-------------|--------------------------------|
| **S**poofing | Suplantación de identidad | Autenticación |
| **T**ampering | Manipulación de datos | Integridad |
| **R**epudiation | Repudio (negar acciones) | No repudio |
| **I**nformation Disclosure | Divulgación de información | Confidencialidad |
| **D**enial of Service | Denegación de servicio | Disponibilidad |
| **E**levation of Privilege | Elevación de privilegios | Autorización |

---

## 🎯 Contexto del Sistema

### Activos Críticos

1. **Datos de Usuarios**
   - Credenciales (contraseñas hasheadas)
   - Información personal (nombres, emails, RUT)
   - Roles y permisos

2. **Datos Académicos**
   - Asignaturas
   - Secciones
   - Horarios de clases
   - Asignaciones docente-asignatura

3. **Datos de Infraestructura**
   - Campus y edificios
   - Salas y capacidades
   - Bloques horarios

4. **Restricciones Horarias**
   - Restricciones de docentes
   - Preferencias de horario

5. **Tokens de Autenticación**
   - Access tokens (JWT)
   - Refresh tokens

### Actores

1. **Administrador**
   - Control total del sistema
   - Gestiona usuarios, recursos académicos e infraestructura

2. **Docente**
   - Gestiona sus propias restricciones horarias
   - Visualiza información académica

3. **Estudiante**
   - Visualiza horarios y asignaturas
   - Acceso limitado solo lectura

4. **Usuario Anónimo**
   - Acceso solo a login/registro
   - Sin acceso a recursos protegidos

5. **Atacante Potencial**
   - Interno o externo
   - Motivación: robo de datos, disrupción, escalación de privilegios

---

## 🔴 S - Spoofing (Suplantación)

### S1: Suplantación de Identidad de Usuario

**Amenaza**: Un atacante obtiene credenciales de usuario legítimo y accede al sistema.

**Vectores de Ataque**:
- Phishing para obtener credenciales
- Keyloggers en dispositivos comprometidos
- Ataques de fuerza bruta
- Credential stuffing (credenciales filtradas de otros sitios)
- Session hijacking (robo de tokens JWT)

**Impacto**: 🔴 ALTO
- Acceso no autorizado a datos personales
- Manipulación de horarios (si es docente)
- Acceso a información académica sensible

**Controles Actuales**:
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT firmados con RS256
- ✅ Rate limiting en endpoint de login
- ✅ Validación de tokens en cada request

**Controles Faltantes**:
- ⏳ Multi-Factor Authentication (MFA)
- ⏳ Account lockout tras intentos fallidos
- ⏳ Alertas de inicio de sesión sospechoso
- ⏳ Geolocalización de sesiones

**Mitigaciones Recomendadas**:
1. **Inmediato**: Implementar account lockout (5 intentos, 15 min lock)
2. **Corto plazo**: Alertas de login desde nuevos dispositivos
3. **Mediano plazo**: Implementar MFA para roles sensibles (admin, docente)
4. **Largo plazo**: Análisis de comportamiento de sesiones

---

### S2: Falsificación de Tokens JWT

**Amenaza**: Atacante intenta crear o modificar tokens JWT para acceder al sistema.

**Vectores de Ataque**:
- Algoritmo None attack (JWT sin firma)
- Key confusion attack (cambiar algoritmo RS256 a HS256)
- Token replay attack
- Modificación de payload si secret es débil

**Impacto**: 🔴 ALTO
- Acceso completo con identidad falsificada
- Escalación de privilegios modificando claim "rol"

**Controles Actuales**:
- ✅ JWT firmados con RS256 (asimétrico)
- ✅ Validación de firma en cada request
- ✅ Verificación de expiración (30 min)
- ✅ Claves RSA de 2048 bits

**Controles Faltantes**:
- ⏳ Token blacklist para invalidación
- ⏳ Binding de token a dispositivo/IP
- ⏳ Rotación automática de claves

**Mitigaciones Recomendadas**:
1. **Inmediato**: Implementar token blacklist en Redis
2. **Corto plazo**: Agregar "jti" (JWT ID) para tracking
3. **Mediano plazo**: Rotación de claves cada 90 días

**Riesgo**: 🟡 MEDIO (controles actuales son sólidos)

---

### S3: Man-in-the-Middle (MitM)

**Amenaza**: Interceptación de comunicaciones entre cliente y servidor.

**Vectores de Ataque**:
- HTTP sin encriptación
- Certificados SSL autofirmados o inválidos
- ARP poisoning en red local
- Rogue WiFi access points

**Impacto**: 🔴 ALTO
- Robo de credenciales en tránsito
- Robo de tokens JWT
- Lectura de datos sensibles

**Controles Actuales**:
- ✅ HTTPS obligatorio en producción
- ✅ HSTS header configurado
- ✅ Tokens solo en headers Authorization (no en URL)

**Controles Faltantes**:
- ⏳ SSL Pinning en app móvil
- ⏳ Certificate Transparency monitoring

**Mitigaciones Recomendadas**:
1. **Inmediato**: Verificar configuración de HTTPS en todos los ambientes
2. **Corto plazo**: Implementar SSL pinning en app móvil
3. **Mediano plazo**: Monitoreo de certificados

**Riesgo**: 🟢 BAJO (HTTPS enforced)

---

## 🟠 T - Tampering (Manipulación)

### T1: Manipulación de Datos en Tránsito

**Amenaza**: Modificación de requests o responses entre cliente y servidor.

**Vectores de Ataque**:
- Interceptar y modificar HTTP requests
- Replay attacks
- Parameter tampering

**Impacto**: 🟠 MEDIO
- Modificación de horarios
- Cambio de datos académicos
- Alteración de restricciones

**Controles Actuales**:
- ✅ HTTPS previene modificación en tránsito
- ✅ JWT firmados previenen modificación de identidad
- ✅ Validación de entrada con Pydantic

**Controles Faltantes**:
- ⏳ Request signing (HMAC de body)
- ⏳ Nonces para prevenir replay

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Implementar timestamps en requests críticos
2. **Mediano plazo**: Request signing para operaciones sensibles

**Riesgo**: 🟡 MEDIO

---

### T2: Manipulación de Datos en Base de Datos

**Amenaza**: Modificación directa o inyección para alterar datos en BD.

**Vectores de Ataque**:
- SQL Injection
- Acceso directo a BD si credenciales comprometidas
- Insider threat (acceso privilegiado malicioso)

**Impacto**: 🔴 ALTO
- Alteración de horarios completos
- Modificación de roles de usuarios
- Eliminación de datos críticos

**Controles Actuales**:
- ✅ SQLAlchemy ORM con prepared statements (previene SQL Injection)
- ✅ Validación de entrada
- ✅ BD solo accesible desde backend (Docker network)
- ✅ Credenciales de BD en variables de entorno

**Controles Faltantes**:
- ⏳ Auditoría completa de cambios en BD
- ⏳ Backups encriptados automatizados
- ⏳ Detección de anomalías en queries

**Mitigaciones Recomendadas**:
1. **Inmediato**: Implementar triggers de auditoría en tablas críticas
2. **Corto plazo**: Backups diarios automatizados
3. **Mediano plazo**: Sistema de auditoría completo con timestamps

**Riesgo**: 🟡 MEDIO (ORM protege contra inyección)

---

### T3: Manipulación de Lógica de Negocio

**Amenaza**: Abusar de la lógica de la aplicación para lograr resultados no intencionados.

**Vectores de Ataque**:
- Race conditions en operaciones concurrentes
- Bypassing de validaciones de negocio
- Overflow de restricciones (ej: crear infinitas restricciones)
- TOCTOU (Time of Check to Time of Use) vulnerabilities

**Impacto**: 🟠 MEDIO
- Doble asignación de recursos
- Conflictos de horarios no detectados
- Bypass de límites de negocio

**Controles Actuales**:
- ✅ Validaciones en use cases
- ✅ Transacciones de BD para atomicidad
- ✅ Validaciones de integridad referencial

**Controles Faltantes**:
- ⏳ Locks optimistas para concurrencia
- ⏳ Límites de tasa por usuario (rate limiting funcional)
- ⏳ Validaciones de estado de negocio

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Implementar límites en cantidad de restricciones por docente
2. **Mediano plazo**: Locks optimistas en operaciones críticas
3. **Mediano plazo**: Validación de estado completo antes de operaciones

**Riesgo**: 🟡 MEDIO

---

## 🟣 R - Repudiation (Repudio)

### R1: Negación de Acciones Realizadas

**Amenaza**: Usuario niega haber realizado una acción (ej: eliminar un horario).

**Vectores de Ataque**:
- Falta de logging de acciones
- Logs pueden ser modificados
- No hay timestamp o user tracking

**Impacto**: 🟡 MEDIO
- Imposibilidad de auditar cambios
- Conflictos sobre quién hizo qué
- Problemas legales o académicos

**Controles Actuales**:
- ✅ Logging de requests HTTP con user_id
- ✅ Logging de autenticación (login, logout)
- ✅ Timestamps en logs

**Controles Faltantes**:
- ⏳ Auditoría completa de operaciones CRUD
- ⏳ Logs inmutables (write-only, append-only)
- ⏳ Digital signatures en logs críticos
- ⏳ Auditoría de cambios en datos sensibles

**Mitigaciones Recomendadas**:
1. **Inmediato**: Implementar tabla de auditoría para operaciones críticas
2. **Corto plazo**: Logging detallado de todas las mutaciones
3. **Mediano plazo**: Logs en sistema externo inmutable (ELK, CloudWatch)
4. **Largo plazo**: Blockchain para auditoría crítica (opcional)

**Riesgo**: 🟡 MEDIO

---

### R2: Modificación de Logs

**Amenaza**: Atacante con acceso al servidor modifica logs para ocultar actividad.

**Vectores de Ataque**:
- Acceso privilegiado al servidor
- Logs en filesystem modificable
- No hay checksum o firma de logs

**Impacto**: 🟠 MEDIO
- Imposibilidad de investigar incidentes
- Encubrimiento de actividad maliciosa

**Controles Actuales**:
- ✅ Logs en directorio con permisos restringidos
- ✅ Logs separados por nivel (INFO, ERROR)

**Controles Faltantes**:
- ⏳ Logs enviados a sistema externo en tiempo real
- ⏳ Checksum o HMAC de archivos de log
- ⏳ Alertas de modificación de logs

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Enviar logs a sistema externo (ELK, Splunk)
2. **Mediano plazo**: Logs inmutables con checksums
3. **Mediano plazo**: Alertas de integridad de logs

**Riesgo**: 🟡 MEDIO

---

## 🔵 I - Information Disclosure (Divulgación de Información)

### I1: Exposición de Datos Sensibles en Logs

**Amenaza**: Datos sensibles (contraseñas, tokens) se loguean sin querer.

**Vectores de Ataque**:
- Logging de request bodies que contienen passwords
- Logging de headers Authorization con tokens
- Stack traces con información sensible

**Impacto**: 🔴 ALTO
- Exposición de credenciales
- Robo de tokens de sesión
- Violación de privacidad

**Controles Actuales**:
- ✅ Middleware de sanitización de logs
- ✅ Filtrado de passwords, tokens en logs
- ✅ No exponer stack traces a clientes

**Controles Faltantes**:
- ⏳ Revisión automática de logs por datos sensibles
- ⏳ PII detection en logs

**Mitigaciones Recomendadas**:
1. **Inmediato**: Auditar todos los logs actuales
2. **Corto plazo**: Regex patterns para detectar leaks en CI/CD
3. **Mediano plazo**: Herramienta de DLP (Data Loss Prevention)

**Riesgo**: 🟢 BAJO (middleware implementado)

---

### I2: Exposición de Información en Mensajes de Error

**Amenaza**: Mensajes de error revelan información sobre estructura de BD, rutas, versiones.

**Vectores de Ataque**:
- Stack traces completos en producción
- Mensajes de error verbosos
- Códigos de error que revelan lógica interna

**Impacto**: 🟠 MEDIO
- Información útil para atacantes
- Enumeración de usuarios
- Discovery de estructura interna

**Controles Actuales**:
- ✅ Mensajes de error genéricos en producción
- ✅ Stack traces solo en desarrollo
- ✅ Códigos HTTP estándar

**Controles Faltantes**:
- ⏳ Mensajes más genéricos en algunos endpoints
- ⏳ Error IDs para tracking interno sin revelar detalles

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Revisar todos los mensajes de error
2. **Corto plazo**: Implementar error IDs únicos
3. **Mediano plazo**: Respuestas uniformes para recursos no encontrados

**Riesgo**: 🟡 MEDIO

---

### I3: Enumeración de Usuarios

**Amenaza**: Descubrir usuarios válidos del sistema mediante respuestas diferentes.

**Vectores de Ataque**:
- Login: "Usuario no existe" vs "Contraseña incorrecta"
- Recuperación de contraseña: "Email no registrado"
- Timing attacks (respuesta más rápida si usuario no existe)

**Impacto**: 🟡 MEDIO
- Lista de emails válidos para phishing
- Información para ataques dirigidos

**Controles Actuales**:
- ✅ Mensaje genérico en login ("Credenciales inválidas")
- ✅ Rate limiting previene enumeración masiva

**Controles Faltantes**:
- ⏳ Timing constante en verificación de credenciales
- ⏳ Respuestas idénticas en recuperación de contraseña

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Timing constante con delays artificiales
2. **Corto plazo**: Mismo mensaje para "email no existe" y "email enviado"

**Riesgo**: 🟡 MEDIO

---

### I4: Exposición de IDs Internos Predecibles

**Amenaza**: IDs secuenciales permiten enumeración de recursos.

**Vectores de Ataque**:
- IDs autoincrementales en URLs
- Iterar sobre IDs para descubrir todos los recursos
- Inferir cantidad de registros

**Impacto**: 🟡 MEDIO
- Enumeración de horarios, usuarios, restricciones
- Información sobre tamaño del sistema

**Controles Actuales**:
- ✅ Control de acceso en cada endpoint (no basta con conocer ID)
- ✅ Validación de autorización antes de retornar recurso

**Controles Faltantes**:
- ⏳ UUIDs en lugar de IDs secuenciales
- ⏳ Ofuscación de IDs

**Mitigaciones Recomendadas**:
1. **Mediano plazo**: Migrar a UUIDs para recursos sensibles
2. **Alternativa**: Hash IDs (hashids library)

**Riesgo**: 🟡 MEDIO (RBAC mitiga impacto)

---

### I5: Fuga de Datos a Través de APIs

**Amenaza**: APIs retornan más información de la necesaria.

**Vectores de Ataque**:
- Respuestas con campos innecesarios
- Endpoints sin paginación (retornan todos los registros)
- Falta de filtrado en listados

**Impacto**: 🟠 MEDIO
- Mass data extraction
- Información sobre otros usuarios

**Controles Actuales**:
- ✅ Paginación implementada (skip/limit)
- ✅ Schemas de respuesta definidos (Pydantic)
- ✅ Control de acceso por rol

**Controles Faltantes**:
- ⏳ Field filtering (seleccionar campos a retornar)
- ⏳ Auditoría de accesos masivos a datos

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Revisar schemas de respuesta, eliminar campos innecesarios
2. **Mediano plazo**: Implementar field selection
3. **Mediano plazo**: Alertas de scraping (muchos requests de listado)

**Riesgo**: 🟡 MEDIO

---

## 🟢 D - Denial of Service (Denegación de Servicio)

### D1: DoS por Rate Exhaustion

**Amenaza**: Atacante hace múltiples requests para agotar recursos del servidor.

**Vectores de Ataque**:
- Request flooding
- Endpoints costosos computacionalmente
- Sin límites de tasa

**Impacto**: 🟠 MEDIO
- Servicio inaccesible
- Degradación de performance
- Costos aumentados de infraestructura

**Controles Actuales**:
- ✅ Rate limiting middleware implementado
- ✅ Límites por usuario y global
- ✅ Límites más estrictos en endpoints de auth

**Controles Faltantes**:
- ⏳ Rate limiting por IP
- ⏳ WAF (Web Application Firewall)
- ⏳ DDoS protection (Cloudflare, AWS Shield)

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Agregar rate limiting por IP
2. **Mediano plazo**: Implementar WAF
3. **Largo plazo**: DDoS protection en CDN

**Riesgo**: 🟡 MEDIO (controles básicos implementados)

---

### D2: Resource Exhaustion (BD)

**Amenaza**: Queries costosas agotan recursos de base de datos.

**Vectores de Ataque**:
- Queries sin límite (listados sin paginación)
- Queries complejas con múltiples joins
- N+1 query problem

**Impacto**: 🟠 MEDIO
- BD inaccesible
- Timeout de requests
- Impacto en todos los usuarios

**Controles Actuales**:
- ✅ Paginación obligatoria
- ✅ Índices en BD
- ✅ Timeout de queries configurado

**Controles Faltantes**:
- ⏳ Query complexity analysis
- ⏳ Connection pooling optimizado
- ⏳ Caching de queries frecuentes

**Mitigaciones Recomendadas**:
1. **Corto plazo**: Revisar y optimizar queries lentas
2. **Mediano plazo**: Implementar caching (Redis)
3. **Mediano plazo**: Query monitoring y alertas

**Riesgo**: 🟡 MEDIO

---

### D3: Application Logic DoS

**Amenaza**: Abusar de lógica de negocio para consumir recursos.

**Vectores de Ataque**:
- Crear cantidad masiva de restricciones
- Generar horarios extremadamente complejos
- Operaciones costosas sin límites

**Impacto**: 🟡 MEDIO
- Performance degradada
- Recursos exhausted
- Impacto en UX

**Controles Actuales**:
- ✅ Validaciones básicas de negocio
- ✅ Timeouts configurados

**Controles Faltantes**:
- ⏳ Límites de cantidad de entidades por usuario
- ⏳ Límites de complejidad de operaciones
- ⏳ Throttling de operaciones pesadas

**Mitigaciones Recomendadas**:
1. **Inmediato**: Límite de restricciones por docente (ej: 50)
2. **Corto plazo**: Límite de secciones por asignatura
3. **Mediano plazo**: Queue system para operaciones pesadas

**Riesgo**: 🟡 MEDIO

---

## 🔴 E - Elevation of Privilege (Elevación de Privilegios)

### E1: Escalación Horizontal (Acceso a Datos de Otros Usuarios)

**Amenaza**: Usuario accede a datos de otro usuario del mismo nivel.

**Vectores de Ataque**:
- Modificar user_id en requests
- Acceder a /users/123 siendo usuario 456
- Modificar restricciones de otro docente

**Impacto**: 🔴 ALTO
- Violación de privacidad
- Acceso a datos personales
- Manipulación de datos de terceros

**Controles Actuales**:
- ✅ Verificación de propiedad en use cases
- ✅ AuthorizationService.verify_can_access_user()
- ✅ AuthorizationService.verify_can_access_restriccion()

**Controles Faltantes**:
- ⏳ Tests exhaustivos de autorización
- ⏳ Auditoría de intentos de acceso no autorizado

**Mitigaciones Recomendadas**:
1. **Inmediato**: Auditar todos los endpoints por IDOR vulnerabilities
2. **Corto plazo**: Tests de autorización en CI/CD
3. **Corto plazo**: Logging de intentos de acceso no autorizado

**Riesgo**: 🟢 BAJO (controles robustos implementados)

---

### E2: Escalación Vertical (Obtener Privilegios de Admin)

**Amenaza**: Usuario normal obtiene privilegios de administrador.

**Vectores de Ataque**:
- Modificar claim "rol" en JWT (si no valida firma)
- Explotar vulnerabilidad en cambio de rol
- Mass assignment vulnerability (cambiar propio rol en update)

**Impacto**: 🔴 CRÍTICO
- Control total del sistema
- Acceso a todos los datos
- Capacidad de modificar cualquier recurso

**Controles Actuales**:
- ✅ JWT firmados (no se puede modificar claim "rol")
- ✅ Usuario no puede cambiar su propio rol
- ✅ Actualización de rol solo por admin
- ✅ Validación estricta en use cases

**Controles Faltantes**:
- ⏳ Alertas de cambios de rol
- ⏳ Auditoría completa de cambios de permisos

**Mitigaciones Recomendadas**:
1. **Inmediato**: Tests específicos de escalación vertical
2. **Corto plazo**: Alertas de cambios de rol por email
3. **Corto plazo**: Logging obligatorio de cambios de permisos

**Riesgo**: 🟢 BAJO (controles robustos)

---

### E3: Bypass de Autorización

**Amenaza**: Atacante encuentra ruta para eludir controles de autorización.

**Vectores de Ataque**:
- Endpoint sin dependency de autorización
- Path traversal en rutas
- Diferencia entre implementación y diseño
- Uso directo de repositorio bypassing use cases

**Impacto**: 🔴 CRÍTICO
- Acceso no autorizado
- Operaciones prohibidas

**Controles Actuales**:
- ✅ Autorización en dependencies de FastAPI
- ✅ Verificación adicional en use cases
- ✅ Code reviews obligatorios

**Controles Faltantes**:
- ⏳ Análisis estático de endpoints sin protección
- ⏳ Tests automatizados de autorización

**Mitigaciones Recomendadas**:
1. **Inmediato**: Auditar todos los endpoints, verificar dependencies
2. **Corto plazo**: Linter custom para detectar endpoints sin auth
3. **Corto plazo**: Tests automatizados de autorización completos

**Riesgo**: 🟡 MEDIO

---

### E4: Privilege Creep

**Amenaza**: Usuarios acumulan permisos innecesarios con el tiempo.

**Vectores de Ataque**:
- Cambios de rol no remueven permisos anteriores
- Permisos temporales que se vuelven permanentes
- Falta de revisión periódica de permisos

**Impacto**: 🟡 MEDIO
- Usuarios con más permisos de los necesarios
- Violación de principio de menor privilegio

**Controles Actuales**:
- ✅ RBAC estricto (no permisos acumulativos)
- ✅ Roles mutuamente exclusivos

**Controles Faltantes**:
- ⏳ Revisión periódica de roles y permisos
- ⏳ Auditoría de uso de permisos
- ⏳ Alertas de permisos no usados

**Mitigaciones Recomendadas**:
1. **Mediano plazo**: Dashboard de auditoría de permisos
2. **Mediano plazo**: Revisión trimestral de roles
3. **Largo plazo**: Automated privilege review

**Riesgo**: 🟡 MEDIO

---

## 📊 Matriz de Riesgos

### Por Categoría STRIDE

| Categoría | Amenazas Totales | Crítico | Alto | Medio | Bajo |
|-----------|------------------|---------|------|-------|------|
| Spoofing | 3 | 0 | 2 | 1 | 0 |
| Tampering | 3 | 0 | 1 | 2 | 0 |
| Repudiation | 2 | 0 | 0 | 2 | 0 |
| Information Disclosure | 5 | 0 | 1 | 3 | 1 |
| Denial of Service | 3 | 0 | 0 | 3 | 0 |
| Elevation of Privilege | 4 | 1 | 1 | 1 | 1 |
| **TOTAL** | **20** | **1** | **5** | **12** | **2** |

### Top 5 Amenazas Prioritarias

| Rank | ID | Amenaza | Riesgo | Mitigación Urgente |
|------|----|---------|---------|--------------------|
| 1 | E2 | Escalación Vertical | 🔴 CRÍTICO | ✅ Mitigado (controles robustos) |
| 2 | S1 | Suplantación de Identidad | 🔴 ALTO | Account lockout + MFA |
| 3 | S2 | Falsificación de JWT | 🔴 ALTO | ✅ Bien mitigado (RS256) |
| 4 | I1 | Exposición de Datos en Logs | 🔴 ALTO | ✅ Mitigado (middleware) |
| 5 | E1 | Escalación Horizontal | 🔴 ALTO | ✅ Bien mitigado (RBAC) |

---

## 🎯 Plan de Acción

### Prioridad Inmediata (Esta Semana)

1. ✅ **E3**: Auditar todos los endpoints por autorización faltante
2. ✅ **S1**: Implementar account lockout (5 intentos, 15 min)
3. ✅ **D3**: Agregar límite de 50 restricciones por docente
4. ✅ **R1**: Implementar tabla de auditoría para operaciones críticas

### Prioridad Alta (Este Mes)

1. **S1**: Alertas de login desde dispositivo nuevo
2. **I3**: Timing constante en autenticación
3. **E3**: Tests automatizados de autorización
4. **T2**: Auditoría de cambios en BD (triggers)
5. **D1**: Rate limiting por IP

### Prioridad Media (Próximo Trimestre)

1. **S1**: Implementar MFA para administradores
2. **S2**: Token blacklist con Redis
3. **R1**: Logs en sistema externo inmutable
4. **I4**: Migrar a UUIDs en recursos sensibles
5. **D2**: Caching con Redis

### Prioridad Baja (Roadmap)

1. **S3**: SSL Pinning en app móvil
2. **T1**: Request signing para operaciones críticas
3. **D1**: WAF y DDoS protection
4. **E4**: Dashboard de auditoría de permisos

---

## 🔄 Mantenimiento

Este análisis de amenazas debe ser:

- **Actualizado** cuando se agreguen nuevas funcionalidades
- **Revisado** trimestralmente por el equipo
- **Validado** tras incidentes de seguridad
- **Presentado** a stakeholders regularmente

---

## 📚 Referencias

- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Microsoft STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP A04:2021 Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)

---

**Última actualización**: 11 de noviembre de 2025  
**Próxima revisión**: Febrero 2026  
**Responsable**: Equipo de Desarrollo SGH
