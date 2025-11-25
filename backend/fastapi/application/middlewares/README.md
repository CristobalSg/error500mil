# Middlewares de Seguridad Transversal

Este módulo contiene los middlewares de seguridad que se aplican globalmente a todas las solicitudes HTTP del backend.

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Middlewares Implementados](#middlewares-implementados)
  - [SecurityLoggingMiddleware](#securityloggingmiddleware)
  - [RateLimitMiddleware](#ratelimitmiddleware)
  - [SanitizationMiddleware](#sanitizationmiddleware)
- [Configuración](#configuración)
- [Orden de Ejecución](#orden-de-ejecución)
- [Logs y Monitoreo](#logs-y-monitoreo)
- [Testing](#testing)

## Descripción General

Los middlewares de seguridad proporcionan capas de protección transversal que se aplican a todas las solicitudes HTTP antes de que lleguen a los endpoints específicos. Esto garantiza que:

1. Todas las solicitudes sean registradas para auditoría
2. Se prevenga el abuso mediante rate limiting
3. Los datos de entrada sean sanitizados para prevenir inyecciones

## Middlewares Implementados

### SecurityLoggingMiddleware

**Propósito**: Registrar todos los eventos de seguridad relevantes para auditoría y monitoreo.

**Características**:
- ✅ Logging estructurado de todas las requests
- ✅ Redacción automática de información sensible (passwords, tokens, etc.)
- ✅ Registro de eventos de seguridad específicos (login, logout, accesos denegados)
- ✅ Métricas de rendimiento (tiempo de procesamiento)
- ✅ Alertas para requests lentas (> 1 segundo)

**Eventos Registrados**:
- Login exitoso/fallido
- Registro de nuevos usuarios
- Intentos de acceso no autorizado (401, 403)
- Errores del servidor (5xx)
- Requests con tiempo de procesamiento alto

**Headers Agregados**:
```
X-Process-Time: 0.123 (tiempo en segundos)
```

**Ejemplo de Log**:
```json
{
  "event": "request_completed",
  "method": "POST",
  "path": "/api/auth/login",
  "client_ip": "192.168.1.100",
  "status_code": 200,
  "process_time_ms": 145.23,
  "is_sensitive": true
}
```

**Campos Sensibles Redactados**:
- password, passwd, pwd, pass
- token, access_token, refresh_token
- secret, api_key, apikey
- credential, auth, authorization

### RateLimitMiddleware

**Propósito**: Prevenir abuso de la API mediante límites de solicitudes por IP.

**Características**:
- ✅ Límite de requests por ventana de tiempo
- ✅ Tracking por IP del cliente
- ✅ Diferentes límites para usuarios autenticados vs no autenticados
- ✅ Limpieza automática de registros antiguos
- ✅ Headers informativos sobre límites
- ✅ Exclusión de endpoints de health check

**Configuración por Defecto**:
```python
requests_limit = 100          # Requests por minuto (no autenticados)
window_seconds = 60           # Ventana de tiempo
auth_requests_limit = 200     # Requests por minuto (autenticados)
cleanup_interval = 300        # Limpieza cada 5 minutos
```

**Endpoints Excluidos**:
- `/api/health`
- `/api/`
- `/api/docs`
- `/api/openapi.json`

**Headers de Respuesta**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1699123456
```

**Respuesta cuando se excede el límite**:
```json
{
  "detail": "Demasiadas solicitudes. Por favor, intenta más tarde.",
  "retry_after": 60
}
```
Status Code: `429 TOO MANY REQUESTS`

**Consideraciones**:
- El tracking es por IP, considerando proxies (`X-Forwarded-For`, `X-Real-IP`)
- Los usuarios autenticados tienen un límite mayor
- La memoria se limpia automáticamente para evitar crecimiento ilimitado

### SanitizationMiddleware

**Propósito**: Validar y sanitizar todas las entradas para prevenir ataques de inyección.

**Características**:
- ✅ Detección de SQL Injection
- ✅ Detección de XSS (Cross-Site Scripting)
- ✅ Detección de Path Traversal
- ✅ Validación de Content-Type
- ✅ Límite de tamaño de payload (5MB)
- ✅ Sanitización recursiva de estructuras JSON

**Patrones Detectados**:

**SQL Injection**:
- `UNION SELECT`, `INSERT INTO`, `UPDATE SET`, `DELETE FROM`
- `DROP TABLE`, `EXEC(`, `EXECUTE(`
- `'; --`, `' OR '1'='1`

**XSS**:
- `<script>`, `javascript:`
- `onerror=`, `onload=`, `onclick=`
- `<iframe>`, `<object>`, `<embed>`

**Path Traversal**:
- `../`, `..`
- `%2e%2e`, `%252e%252e`

**Validaciones**:
- Content-Type debe ser: `application/json`, `application/x-www-form-urlencoded`, o `multipart/form-data`
- Payload máximo: 5MB
- Sanitización de query params, path params y body

**Respuestas de Error**:

```json
// Content-Type inválido
{
  "detail": "Content-Type no soportado"
}
// Status: 415 UNSUPPORTED MEDIA TYPE

// Payload muy grande
{
  "detail": "Payload demasiado grande"
}
// Status: 413 REQUEST ENTITY TOO LARGE

// Datos sospechosos
{
  "detail": "Body contiene datos sospechosos"
}
// Status: 400 BAD REQUEST
```

## Configuración

Los middlewares se configuran en `main.py`:

```python
from application.middlewares import (
    SanitizationMiddleware,
    RateLimitMiddleware,
    SecurityLoggingMiddleware
)

# El orden es importante!
app.add_middleware(SecurityLoggingMiddleware, ...)
app.add_middleware(RateLimitMiddleware, ...)
app.add_middleware(SanitizationMiddleware, ...)
app.add_middleware(CORSMiddleware, ...)
```

### Personalizar Configuración

**SecurityLoggingMiddleware**:
```python
app.add_middleware(
    SecurityLoggingMiddleware,
    log_request_body=False,        # No loggear bodies por seguridad
    log_response_body=False,       # No loggear respuestas
    enable_performance_logging=True # Alertar requests lentas
)
```

**RateLimitMiddleware**:
```python
app.add_middleware(
    RateLimitMiddleware,
    requests_limit=100,           # Límite para no autenticados
    window_seconds=60,            # Ventana de 1 minuto
    auth_requests_limit=200,      # Límite para autenticados
    cleanup_interval=300          # Limpiar cada 5 minutos
)
```

**SanitizationMiddleware**:
```python
app.add_middleware(
    SanitizationMiddleware,
    enable_sql_check=True,        # Detectar SQL injection
    enable_xss_check=True,        # Detectar XSS
    enable_path_check=True        # Detectar path traversal
)
```

## Orden de Ejecución

El orden de los middlewares es **crucial**. Se ejecutan en orden inverso al que se agregan:

```
Request → SecurityLogging → RateLimit → Sanitization → CORS → Endpoint
Response ← SecurityLogging ← RateLimit ← Sanitization ← CORS ← Endpoint
```

**Orden Recomendado**:
1. **SecurityLoggingMiddleware**: Primero para capturar TODO
2. **RateLimitMiddleware**: Segundo para bloquear abuso temprano
3. **SanitizationMiddleware**: Tercero para validar datos
4. **CORSMiddleware**: Último middleware de seguridad

## Logs y Monitoreo

Los logs se almacenan en `/app/logs/`:

```
/app/logs/
├── app.log           # Logs generales
├── errors.log        # Solo errores (level ERROR+)
└── security.log      # Eventos de seguridad
```

### Formato de Logs

```
2025-11-04 10:30:45 - security - INFO - SECURITY EVENT: Successful login from 192.168.1.100 (took 0.12s)
2025-11-04 10:31:20 - security - WARNING - Rate limit excedido para IP 192.168.1.50 (autenticado: False)
2025-11-04 10:32:15 - security - WARNING - Posible SQL Injection detectado en campo 'email': patrón 'union.*select' desde 192.168.1.75
```

### Monitorear Logs

**Ver logs en tiempo real**:
```bash
# Logs generales
docker compose --env-file .env.development exec backend tail -f /app/logs/app.log

# Logs de seguridad
docker compose --env-file .env.development exec backend tail -f /app/logs/security.log

# Logs de errores
docker compose --env-file .env.development exec backend tail -f /app/logs/errors.log
```

**Buscar eventos específicos**:
```bash
# Login fallidos
docker compose --env-file .env.development exec backend grep "Failed login" /app/logs/security.log

# Rate limiting
docker compose --env-file .env.development exec backend grep "Rate limit" /app/logs/security.log

# SQL Injection attempts
docker compose --env-file .env.development exec backend grep "SQL Injection" /app/logs/security.log
```

## Testing

### Probar Rate Limiting

```bash
# Hacer múltiples requests rápidas
for i in {1..150}; do
  curl -X GET http://localhost:8000/api/health
done
```

Después de 100 requests deberías recibir un `429 TOO MANY REQUESTS`.

### Probar Sanitización

**SQL Injection**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin\"; DROP TABLE users; --", "password": "test"}'
```

Debería retornar `400 BAD REQUEST` con mensaje de datos sospechosos.

**XSS**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "<script>alert(1)</script>", "password": "test"}'
```

Debería retornar `400 BAD REQUEST`.

### Verificar Logging

```bash
# Hacer login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "correctpassword"}'

# Verificar log
docker compose --env-file .env.development exec backend tail -5 /app/logs/security.log
```

Deberías ver un evento de login registrado.

## Mejores Prácticas

1. **No deshabilitar middlewares en producción**: Todos son esenciales para seguridad
2. **Monitorear logs regularmente**: Revisar `security.log` para detectar ataques
3. **Ajustar rate limits según tráfico**: Comenzar conservador y ajustar según necesidad
4. **Rotar logs**: Implementar rotación para evitar crecimiento ilimitado
5. **Alertas automáticas**: Configurar alertas para eventos sospechosos frecuentes

## Problemas Comunes

### Rate Limit muy restrictivo

**Síntoma**: Usuarios legítimos reciben 429
**Solución**: Aumentar `requests_limit` o `window_seconds`

### Falsos positivos en sanitización

**Síntoma**: Requests válidas son bloqueadas
**Solución**: Revisar patrones en `SanitizationMiddleware` y ajustar si es necesario

### Logs crecen mucho

**Síntoma**: Disco lleno
**Solución**: Implementar rotación de logs con `logrotate` o similar

## Roadmap Futuro

- [ ] Persistencia de rate limiting en Redis para múltiples instancias
- [ ] Machine learning para detectar patrones de ataque
- [ ] Dashboard de monitoreo en tiempo real
- [ ] Integración con sistemas SIEM
- [ ] Blacklist automática de IPs sospechosas
- [ ] Whitelist para IPs confiables
