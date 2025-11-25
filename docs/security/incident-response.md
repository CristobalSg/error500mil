# 🚨 Plan de Respuesta a Incidentes de Seguridad

## Propósito

Este documento establece los procedimientos para responder efectivamente a incidentes de seguridad en el Sistema de Gestión Horaria (SGH), minimizando el impacto y facilitando la recuperación rápida.

---

## 📋 Definiciones

### ¿Qué es un Incidente de Seguridad?

Un evento o serie de eventos que:
- Compromete la confidencialidad, integridad o disponibilidad del sistema
- Viola políticas de seguridad
- Expone datos sensibles
- Interrumpe operaciones normales

### Ejemplos de Incidentes

- ✅ Acceso no autorizado a cuentas de usuario
- ✅ Exposición de credenciales o tokens
- ✅ Exfiltración masiva de datos
- ✅ Ataque de denegación de servicio
- ✅ Inyección SQL exitosa
- ✅ Escalación de privilegios
- ✅ Compromiso de servidor
- ✅ Phishing exitoso contra usuarios

---

## 🎯 Objetivos del Plan

1. **Detectar** incidentes rápidamente
2. **Contener** el impacto del incidente
3. **Erradicar** la amenaza
4. **Recuperar** operaciones normales
5. **Aprender** del incidente para prevenir recurrencia

---

## 👥 Equipo de Respuesta a Incidentes (IRT)

### Roles y Responsabilidades

| Rol | Responsabilidad | Contacto |
|-----|----------------|----------|
| **Incident Commander** | Coordina respuesta, toma decisiones | [TBD] |
| **Tech Lead** | Análisis técnico, remediación | [TBD] |
| **DevOps Lead** | Infraestructura, logs, recuperación | [TBD] |
| **Security Lead** | Análisis de amenazas, forensics | [TBD] |
| **Communications Lead** | Comunicación interna/externa | [TBD] |
| **Legal/Compliance** | Aspectos legales, notificaciones | [TBD] |

### Escalación

```
┌─────────────────────────────────┐
│  Nivel 1: Desarrollador         │
│  • Detecta anomalía             │
│  • Reporta a Tech Lead          │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Nivel 2: Tech Lead             │
│  • Evalúa severidad             │
│  • Activa IRT si es crítico     │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Nivel 3: Incident Commander    │
│  • Coordina respuesta completa  │
│  • Comunica a stakeholders      │
└─────────────────────────────────┘
```

---

## 🚦 Clasificación de Severidad

### Matriz de Severidad

| Nivel | Criterios | Tiempo de Respuesta | Escalación |
|-------|-----------|---------------------|------------|
| **🔴 CRÍTICO** | • Acceso root comprometido<br>• Exfiltración masiva de datos<br>• Sistema completamente inaccesible<br>• Vulnerabilidad 0-day explotada | **15 minutos** | Inmediata |
| **🟠 ALTO** | • Acceso admin comprometido<br>• Pérdida de datos limitada<br>• DoS parcial<br>• Vulnerabilidad crítica descubierta | **1 hora** | Tech Lead |
| **🟡 MEDIO** | • Acceso no autorizado a cuenta regular<br>• Intento de ataque detectado y bloqueado<br>• Vulnerabilidad media descubierta | **4 horas** | Opcional |
| **🟢 BAJO** | • Intento fallido de acceso<br>• Anomalía sin impacto<br>• Vulnerabilidad baja | **24 horas** | No requerida |

---

## 📞 Proceso de Reporte

### Cómo Reportar un Incidente

#### 1. Detección

**¿Qué buscar?**
- Alertas automáticas del sistema
- Logs inusuales
- Comportamiento anómalo de usuarios
- Reportes de usuarios
- Hallazgos de security scans
- Reportes de terceros

#### 2. Reporte Inmediato

**Vía prioritaria** (incidentes críticos/altos):
- 🚨 Canal Slack: `#security-incidents`
- 📧 Email: `security@[domain].com`
- 📱 Teléfono: [Número de emergencia]

**Información mínima requerida**:
```
REPORTE DE INCIDENTE DE SEGURIDAD

Fecha/Hora: [ISO timestamp]
Reportado por: [Nombre]
Severidad estimada: [CRÍTICO/ALTO/MEDIO/BAJO]

DESCRIPCIÓN:
[Qué ocurrió]

EVIDENCIA:
[Logs, screenshots, IPs, etc.]

IMPACTO:
[Sistemas afectados, usuarios, datos]

ACCIONES INMEDIATAS TOMADAS:
[Si aplica]
```

#### 3. No hacer

❌ **NO** intentar investigar más allá de lo necesario para el reporte  
❌ **NO** borrar evidencia (logs, archivos)  
❌ **NO** informar públicamente hasta que IRT lo autorice  
❌ **NO** intentar "arreglar" sin coordinación  

---

## 🔄 Fases de Respuesta (PICERL)

### Fase 1: Preparación

**Antes del incidente**:
- ✅ Mantener documentación actualizada
- ✅ Realizar drills periódicos (trimestrales)
- ✅ Mantener contactos actualizados
- ✅ Tener herramientas listas
- ✅ Backups verificados y funcionales

### Fase 2: Identificación

**Objetivo**: Confirmar y clasificar el incidente

**Acciones**:
1. **Verificar**: ¿Es realmente un incidente?
2. **Clasificar**: Determinar severidad (usar matriz)
3. **Documentar**: Iniciar timeline del incidente
4. **Notificar**: Activar IRT según severidad
5. **Preservar evidencia**: No borrar logs, capturas de estado

**Timeline máximo**: 
- 🔴 Crítico: 15 min
- 🟠 Alto: 1 hora
- 🟡 Medio: 4 horas

**Checklist**:
```
[ ] Incidente confirmado
[ ] Severidad asignada
[ ] IRT notificado
[ ] Timeline iniciado
[ ] Evidencia preservada
[ ] Sistemas afectados identificados
[ ] Alcance inicial estimado
```

---

### Fase 3: Contención

**Objetivo**: Limitar el daño y prevenir propagación

#### Contención Inmediata

**Para compromiso de cuenta**:
```bash
# 1. Deshabilitar cuenta comprometida
PUT /api/v1/admin/users/{user_id}
{ "is_active": false }

# 2. Invalidar todos los tokens del usuario
# (requiere implementar blacklist)

# 3. Forzar cierre de sesiones
# (requiere implementar session management)
```

**Para ataque DoS activo**:
```bash
# 1. Identificar IP atacante
grep "rate_limit_exceeded" /var/log/sgh/access.log | awk '{print $1}' | sort | uniq -c

# 2. Bloquear IP en firewall
sudo ufw deny from <IP_ATACANTE>

# 3. Activar modo de rate limiting agresivo
# (configurar en middleware)
```

**Para inyección SQL**:
```bash
# 1. Identificar endpoint vulnerable
# 2. Deshabilitar endpoint temporalmente
# 3. Revisar logs de BD para detectar exfiltración
psql -U sgh -d sgh_db -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# 4. Analizar queries sospechosas
```

**Para exposición de secretos**:
```bash
# 1. Rotar TODOS los secretos comprometidos INMEDIATAMENTE
# 2. Generar nuevos JWT secrets
openssl genpkey -algorithm RSA -out jwt_private_new.pem -pkeyopt rsa_keygen_bits:2048

# 3. Actualizar en todos los ambientes
# 4. Invalidar todos los tokens JWT existentes

# 5. Notificar a usuarios de cambio forzado de contraseña
```

#### Contención Completa

**Objetivo**: Eliminar acceso del atacante por completo

**Checklist**:
```
[ ] Acceso del atacante bloqueado
[ ] Cuentas comprometidas deshabilitadas
[ ] Secretos comprometidos rotados
[ ] Vulnerabilidad parchada (temporal)
[ ] Backups recientes verificados
[ ] Sistemas aislados si es necesario
[ ] Monitoreo intensificado activo
```

---

### Fase 4: Erradicación

**Objetivo**: Eliminar la causa raíz del incidente

**Acciones por tipo de incidente**:

#### Vulnerabilidad en Código
1. Identificar código vulnerable
2. Desarrollar parche
3. Revisar código relacionado
4. Testing exhaustivo
5. Desplegar a producción
6. Verificar resolución

#### Configuración Insegura
1. Identificar misconfiguration
2. Aplicar configuración segura
3. Documentar cambio
4. Verificar en todos los ambientes

#### Malware/Backdoor
1. Identificar archivos/procesos maliciosos
2. Eliminar completamente
3. Escanear sistema completo
4. Reinstalar desde backup limpio si es necesario

**Checklist**:
```
[ ] Causa raíz identificada
[ ] Vulnerabilidad eliminada
[ ] Código/config auditado
[ ] Tests de seguridad pasando
[ ] Sistemas escaneados (limpio)
[ ] Documentación actualizada
```

---

### Fase 5: Recuperación

**Objetivo**: Restaurar operaciones normales de manera segura

**Acciones**:

1. **Verificar Integridad**
   ```bash
   # Verificar integridad de archivos
   # Comparar con versión conocida buena
   diff -r /backup/clean/ /app/current/
   
   # Verificar integridad de BD
   # Ejecutar queries de validación
   ```

2. **Restaurar Servicios**
   ```bash
   # Orden recomendado:
   # 1. Base de datos
   # 2. Backend API
   # 3. Frontend
   # 4. Servicios auxiliares
   
   # Monitorear logs durante restauración
   tail -f /var/log/sgh/*.log
   ```

3. **Habilitar Cuentas**
   ```bash
   # Re-habilitar cuentas legítimas
   # Forzar cambio de contraseña
   # Verificar actividad post-habilitación
   ```

4. **Monitoreo Intensificado**
   - Primeras 24h: Monitoreo continuo
   - Siguiente semana: Revisión cada 4h
   - Próximo mes: Revisión diaria

**Checklist**:
```
[ ] Integridad de sistemas verificada
[ ] Servicios restaurados
[ ] Funcionalidad validada
[ ] Usuarios notificados
[ ] Monitoreo intensificado activo
[ ] Métricas normales restauradas
[ ] Stakeholders informados
```

---

### Fase 6: Lecciones Aprendidas

**Objetivo**: Mejorar respuesta futura y prevenir recurrencia

**Actividades**:

1. **Post-Mortem Meeting** (dentro de 72h del incidente)
   - Participantes: IRT completo
   - Duración: 1-2 horas
   - Facilitador: Incident Commander

2. **Documentación**
   ```markdown
   # Post-Mortem: [Título del Incidente]
   
   ## Resumen Ejecutivo
   [2-3 párrafos]
   
   ## Timeline
   | Timestamp | Evento | Responsable | Acción |
   |-----------|--------|-------------|--------|
   
   ## Impacto
   - Usuarios afectados: [número]
   - Datos comprometidos: [detalles]
   - Tiempo de inactividad: [duración]
   - Costo estimado: [si aplica]
   
   ## Causa Raíz
   [Análisis 5 Whys]
   
   ## Qué Funcionó Bien
   - [Punto 1]
   - [Punto 2]
   
   ## Qué Podemos Mejorar
   - [Punto 1]
   - [Punto 2]
   
   ## Acciones Correctivas
   | Acción | Responsable | Fecha Límite | Estado |
   |--------|-------------|--------------|--------|
   
   ## Prevención Futura
   [Recomendaciones]
   ```

3. **Actualizar Documentación**
   - Actualizar este IR plan
   - Actualizar runbooks
   - Actualizar threat model
   - Actualizar controles de seguridad

4. **Implementar Mejoras**
   - Crear tickets de mejora
   - Priorizar según impacto
   - Asignar responsables
   - Tracking de implementación

**Checklist**:
```
[ ] Post-mortem realizado
[ ] Documentación completa
[ ] Causa raíz documentada
[ ] Acciones correctivas identificadas
[ ] Responsables asignados
[ ] Fechas comprometidas
[ ] Documentación actualizada
[ ] Knowledge base actualizado
[ ] Equipo entrenado en lecciones
```

---

## 📊 Playbooks por Tipo de Incidente

### 🔓 Playbook: Compromiso de Cuenta

**Severidad Típica**: 🟠 ALTO (🔴 CRÍTICO si es admin)

**Indicadores**:
- Login desde ubicación inusual
- Múltiples logins fallidos seguidos de éxito
- Actividad fuera de horario normal
- Cambios de configuración no autorizados

**Respuesta**:

1. **Inmediato** (0-15 min):
   ```
   [ ] Deshabilitar cuenta: PUT /api/v1/admin/users/{id} {"is_active": false}
   [ ] Invalidar tokens (si implementado)
   [ ] Notificar al usuario legítimo
   [ ] Revisar actividad reciente en logs
   [ ] Identificar accesos/cambios realizados
   ```

2. **Contención** (15-60 min):
   ```
   [ ] Analizar otros accesos desde misma IP
   [ ] Verificar si hay otras cuentas comprometidas
   [ ] Bloquear IP atacante si es externa
   [ ] Revisar cambios realizados por cuenta
   [ ] Revertir cambios maliciosos
   ```

3. **Erradicación** (1-4 horas):
   ```
   [ ] Determinar cómo se obtuvo acceso (phishing, leak, brute force)
   [ ] Mitigar vulnerabilidad utilizada
   [ ] Escanear sistema por backdoors
   [ ] Forzar reset de password
   ```

4. **Recuperación** (4-24 horas):
   ```
   [ ] Contactar usuario para verificar identidad
   [ ] Usuario cambia contraseña (verificado)
   [ ] Re-habilitar cuenta
   [ ] Monitorear actividad post-recuperación
   [ ] Verificar configuración de MFA (si aplica)
   ```

5. **Seguimiento**:
   ```
   [ ] Educar usuario sobre seguridad
   [ ] Revisar políticas de contraseñas
   [ ] Considerar MFA obligatorio
   ```

---

### 💉 Playbook: Inyección SQL Detectada

**Severidad Típica**: 🔴 CRÍTICO

**Indicadores**:
- Queries SQL en logs de aplicación
- Errores de SQL en logs
- Alertas de WAF (si existe)
- Patrones de ataque en inputs

**Respuesta**:

1. **Inmediato** (0-15 min):
   ```
   [ ] Identificar endpoint vulnerable
   [ ] Deshabilitar endpoint temporalmente
   [ ] Bloquear IP atacante
   [ ] Revisar logs de BD para detectar exfiltración
   [ ] Preservar evidencia (logs completos)
   ```

2. **Contención** (15-30 min):
   ```
   [ ] Analizar queries ejecutadas
   [ ] Determinar si hubo exfiltración de datos
   [ ] Identificar tablas/datos accedidos
   [ ] Verificar integridad de datos
   [ ] Buscar indicios de modificación/eliminación
   ```

3. **Erradicación** (30 min - 2 horas):
   ```
   [ ] Revisar código del endpoint vulnerable
   [ ] Implementar fix (usar ORM correctamente)
   [ ] Code review del fix
   [ ] Testing exhaustivo
   [ ] Desplegar parche
   [ ] Verificar fix efectivo
   ```

4. **Recuperación** (2-4 horas):
   ```
   [ ] Restaurar datos si fueron modificados (desde backup)
   [ ] Re-habilitar endpoint
   [ ] Monitoreo intensificado
   [ ] Auditar otros endpoints similares
   ```

5. **Seguimiento**:
   ```
   [ ] SAST scan completo del código
   [ ] Implementar WAF si no existe
   [ ] Training de equipo sobre SQL injection
   [ ] Implementar input validation adicional
   ```

---

### 🚫 Playbook: Ataque DDoS/DoS

**Severidad Típica**: 🟠 ALTO

**Indicadores**:
- Aumento súbito de tráfico
- Servicios lentos o inaccesibles
- Logs llenos de requests de pocas IPs
- Alertas de rate limiting

**Respuesta**:

1. **Inmediato** (0-5 min):
   ```
   [ ] Verificar que es realmente ataque (no spike legítimo)
   [ ] Identificar IPs atacantes
   [ ] Activar rate limiting agresivo
   [ ] Notificar a equipo DevOps
   ```

2. **Contención** (5-30 min):
   ```
   [ ] Bloquear IPs atacantes en firewall
   [ ] Activar DDoS protection (Cloudflare/AWS Shield)
   [ ] Escalar infraestructura si es necesario
   [ ] Activar WAF con reglas anti-DDoS
   [ ] Considerar activar CAPTCHA temporal
   ```

3. **Monitoreo** (durante ataque):
   ```
   [ ] Monitorear métricas (CPU, memoria, network)
   [ ] Identificar nuevas IPs atacantes
   [ ] Ajustar reglas de bloqueo
   [ ] Mantener comunicación con stakeholders
   ```

4. **Recuperación** (post-ataque):
   ```
   [ ] Remover restricciones temporales gradualmente
   [ ] Analizar logs para entender patrón
   [ ] Verificar integridad del sistema
   [ ] Restaurar configuración normal
   ```

5. **Seguimiento**:
   ```
   [ ] Implementar DDoS protection permanente
   [ ] Mejorar rate limiting
   [ ] Considerar CDN
   [ ] Plan de escalado automático
   ```

---

### 🔑 Playbook: Exposición de Secretos

**Severidad Típica**: 🔴 CRÍTICO

**Indicadores**:
- Secreto encontrado en GitHub/público
- Alerta de secret scanning
- Reporte de tercero
- Secreto en logs

**Respuesta**:

1. **Inmediato** (0-30 min):
   ```
   [ ] Verificar qué secreto fue expuesto
   [ ] Determinar alcance (¿qué puede hacer con este secreto?)
   [ ] Rotar secreto INMEDIATAMENTE
   [ ] Invalidar credenciales/tokens relacionados
   [ ] Notificar a IRT completo
   ```

2. **Contención** (30 min - 2 horas):
   ```
   [ ] Revisar logs para detectar uso del secreto
   [ ] Identificar si hubo acceso no autorizado
   [ ] Revocar acceso obtenido con secreto
   [ ] Actualizar secreto en TODOS los ambientes
   [ ] Verificar que secreto viejo ya no funciona
   ```

3. **Erradicación** (2-4 horas):
   ```
   [ ] Remover secreto de historial de Git (BFG Repo Cleaner)
   [ ] Invalidar cachés que puedan contener secreto
   [ ] Escanear código completo por otros secretos
   [ ] Implementar pre-commit hooks para prevención
   [ ] Contactar GitHub/plataforma para eliminar forks
   ```

4. **Recuperación** (4-24 horas):
   ```
   [ ] Monitorear uso de nuevos secretos
   [ ] Verificar que no haya accesos sospechosos
   [ ] Auditar todos los sistemas accesibles con ese secreto
   [ ] Forzar re-deploy con nuevos secretos
   ```

5. **Seguimiento**:
   ```
   [ ] Implementar secret scanning en CI/CD
   [ ] Migrar a secret manager (Vault, AWS Secrets Manager)
   [ ] Training sobre manejo de secretos
   [ ] Políticas de rotación automática
   ```

---

## 🛠️ Herramientas y Recursos

### Herramientas de Investigación

| Herramienta | Uso | Ubicación |
|-------------|-----|-----------|
| **Logs de Aplicación** | Revisar actividad | `/var/log/sgh/` o CloudWatch |
| **Logs de BD** | Queries ejecutadas | PostgreSQL logs |
| **Logs de Acceso** | Requests HTTP | Nginx/ALB logs |
| **Logs de Sistema** | Actividad de servidor | `/var/log/syslog` |
| **psql** | Investigar BD | `psql -U sgh -d sgh_db` |
| **grep/awk** | Búsqueda en logs | Terminal |
| **tcpdump** | Captura de red | `tcpdump -i eth0` |
| **Wireshark** | Análisis de tráfico | Desktop |

### Comandos Útiles

```bash
# Ver logs de aplicación en tiempo real
tail -f /var/log/sgh/app.log

# Buscar IPs con más requests
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Buscar intentos de inyección SQL
grep -i "select\|union\|drop\|insert" /var/log/sgh/app.log

# Ver procesos sospechosos
ps aux | grep -v "root\|www-data"

# Verificar conexiones de red activas
netstat -tuln | grep ESTABLISHED

# Verificar integridad de archivos
find /app -type f -exec sha256sum {} \; > checksums.txt

# Comparar con checksums conocidos buenos
diff checksums.txt checksums_known_good.txt
```

---

## 📞 Contactos de Emergencia

### Interno

| Rol | Nombre | Email | Teléfono | Disponibilidad |
|-----|--------|-------|----------|----------------|
| Incident Commander | [TBD] | [TBD] | [TBD] | 24/7 |
| Tech Lead | [TBD] | [TBD] | [TBD] | Business hours + on-call |
| DevOps Lead | [TBD] | [TBD] | [TBD] | 24/7 |
| Security Lead | [TBD] | [TBD] | [TBD] | Business hours + on-call |

### Externo

| Servicio | Contacto | Cuándo Contactar |
|----------|----------|------------------|
| Hosting Provider | [TBD] | Infraestructura comprometida |
| Cloud Provider (AWS/GCP) | [TBD] | Recursos cloud comprometidos |
| CERT Nacional | [TBD] | Incidentes mayores, coordinación |
| Legal/Compliance | [TBD] | Violaciones de regulaciones |
| Relaciones Públicas | [TBD] | Incidentes públicos |

---

## 📝 Templates de Comunicación

### Template: Notificación Interna (IRT)

```
Asunto: [SEVERIDAD] Incidente de Seguridad - [BREVE DESCRIPCIÓN]

INCIDENTE DE SEGURIDAD DETECTADO

Severidad: [CRÍTICO/ALTO/MEDIO/BAJO]
Detectado: [Timestamp]
Reportado por: [Nombre]

DESCRIPCIÓN:
[Qué ocurrió en 2-3 oraciones]

SISTEMAS AFECTADOS:
- [Sistema 1]
- [Sistema 2]

IMPACTO ESTIMADO:
[Usuarios/datos/servicios afectados]

ESTADO ACTUAL:
[Contenido/En investigación/Recuperando]

ACCIONES REQUERIDAS:
- [Acción 1] - [Responsable]
- [Acción 2] - [Responsable]

PRÓXIMA ACTUALIZACIÓN: [Timestamp]

War Room: [Slack channel / Meeting link]
```

### Template: Notificación a Usuarios

```
Asunto: Notificación de Seguridad - Sistema de Gestión Horaria

Estimado/a usuario/a,

Queremos informarte sobre un incidente de seguridad que afectó 
al Sistema de Gestión Horaria.

QUÉ OCURRIÓ:
[Descripción clara, no técnica]

QUÉ DATOS FUERON AFECTADOS:
[Específico pero sin alarmar innecesariamente]

QUÉ HEMOS HECHO:
- [Acción 1]
- [Acción 2]

QUÉ DEBES HACER:
- [Acción requerida del usuario, ej: cambiar contraseña]
- [Timeframe]

QUÉ ESTAMOS HACIENDO PARA PREVENIR FUTURO:
[Medidas tomadas]

Si tienes preguntas o preocupaciones, contáctanos en:
[Email de soporte]

Gracias por tu comprensión.

Equipo SGH
```

---

## 📊 Métricas y KPIs

### Métricas de Respuesta

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Tiempo de Detección | < 15 min (crítico) | Desde inicio hasta reporte |
| Tiempo de Respuesta | < 30 min (crítico) | Desde reporte hasta primera acción |
| Tiempo de Contención | < 2 horas (crítico) | Desde respuesta hasta contenido |
| Tiempo de Recuperación | < 24 horas | Desde contención hasta operación normal |
| Post-mortem completado | < 72 horas | Desde resolución hasta documentado |

### Dashboard de Incidentes

```
Incidentes en Últimos 12 Meses:

Críticos:     ██ 2
Altos:        ████ 4
Medios:       ██████ 6
Bajos:        ████████████ 12
              ─────────────────────
Total:        24

Tiempo Promedio de Respuesta:
Críticos:  23 min ✅ (objetivo: 30 min)
Altos:     52 min 🟡 (objetivo: 60 min)
Medios:    3.2 hrs ✅ (objetivo: 4 hrs)
Bajos:     18 hrs ✅ (objetivo: 24 hrs)
```

---

## 🎓 Entrenamiento y Drills

### Drills Regulares

| Tipo | Frecuencia | Duración | Participantes |
|------|------------|----------|---------------|
| Tabletop Exercise | Trimestral | 2 horas | IRT completo |
| Simulación de Compromiso | Semestral | 4 horas | IRT + Dev team |
| War Game | Anual | 1 día | Toda organización |

### Escenarios de Práctica

1. **Compromiso de cuenta admin**
2. **Inyección SQL con exfiltración**
3. **Ataque DDoS durante horario pico**
4. **Exposición de JWT secret**
5. **Ransomware en servidor**

---

## ✅ Checklist de Preparación

### Preparación Técnica

```
[ ] Backups automatizados y probados
[ ] Logs centralizados y persistentes
[ ] Monitoring y alertas configuradas
[ ] Runbooks documentados y actualizados
[ ] Herramientas de forensics disponibles
[ ] Cuentas de emergencia configuradas
[ ] Contact list actualizada
[ ] War room (Slack channel) creado
```

### Preparación de Equipo

```
[ ] Roles de IRT asignados
[ ] Contact information actualizada
[ ] Entrenamiento completado
[ ] Drills realizados este trimestre
[ ] Post-mortems de incidentes anteriores revisados
[ ] Acceso a herramientas verificado
[ ] Proceso de escalación entendido
```

---

## 📚 Referencias y Recursos

- [NIST Computer Security Incident Handling Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf)
- [SANS Incident Handler's Handbook](https://www.sans.org/reading-room/whitepapers/incident/incident-handlers-handbook-33901)
- [OWASP Incident Response Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Incident_Response_Cheat_Sheet.html)

---

## 🔄 Mantenimiento de este Plan

Este plan debe ser:
- **Revisado** trimestralmente
- **Actualizado** después de cada incidente
- **Practicado** mediante drills regulares
- **Mejorado** basado en lecciones aprendidas

**Última actualización**: 11 de noviembre de 2025  
**Próxima revisión programada**: Febrero 2026  
**Owner**: Security Lead / Tech Lead  
**Versión**: 1.0

---

**Este es un documento vivo. Si encuentras información desactualizada o tienes sugerencias de mejora, por favor actualízalo o notifica al Security Lead.**
