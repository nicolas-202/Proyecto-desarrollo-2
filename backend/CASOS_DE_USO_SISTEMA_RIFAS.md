# ANÁLISIS DE CASOS DE USO - SISTEMA DE RIFAS ONLINE

## RESUMEN EJECUTIVO

Este documento presenta el análisis completo de casos de uso del sistema de rifas online basado en Django REST Framework. El sistema permite la gestión integral de rifas, usuarios, tickets y transacciones con un enfoque en la seguridad y transparencia.

**🔒 SISTEMA DE ESCROW (CUENTA CONJUNTA)**: El sistema utiliza una cuenta administrada centralmente que actúa como escrow/garantía. Todo el dinero de las ventas de tickets se deposita en esta cuenta conjunta, asegurando que siempre haya fondos disponibles para premios y reembolsos. Este diseño protege a los participantes y garantiza la integridad del sistema.

## ARQUITECTURA DEL SISTEMA

### 💰 FLUJO FINANCIERO (SISTEMA DE ESCROW)

El sistema implementa un **modelo de cuenta conjunta** que actúa como escrow para garantizar la seguridad de todas las transacciones:

#### **Compra de Tickets:**
```
Comprador → [Método de Pago] → CUENTA CONJUNTA (Escrow)
```
- Todo el dinero de ventas se deposita en la cuenta administrada por el sistema
- Garantiza disponibilidad de fondos para premios y reembolsos
- Proporciona auditoría centralizada de todas las transacciones

#### **Sorteo Exitoso con Ganancias:**
```
INGRESOS > PREMIO:
Cuenta Conjunta → Ganador (premio)
Cuenta Conjunta → Organizador (ganancias)
```

#### **Sorteo con Déficit:**
```
INGRESOS < PREMIO:
1. Sistema valida: ¿Organizador tiene fondos para cubrir déficit?
2. SI → Organizador → Cuenta Conjunta (cubre déficit)
        Cuenta Conjunta → Ganador (premio completo)
3. NO → Sistema cancela rifa automáticamente
        Cuenta Conjunta → Todos los compradores (reembolso total)
```

#### **Ventajas del Sistema de Escrow:**
- ✅ **Protección total de participantes**: Siempre hay fondos disponibles
- ✅ **Prevención de fraude**: El organizador no puede manipular fondos antes del sorteo
- ✅ **Auditoría centralizada**: Todas las transacciones son rastreables
- ✅ **Reembolsos garantizados**: Si algo falla, los participantes recuperan su dinero
- ✅ **Responsabilidad del organizador**: Debe cubrir déficits o la rifa se cancela

### Módulos Principales:
- **User Management**: Gestión de usuarios y autenticación
- **Raffle Management**: Creación y administración de rifas
- **Ticket Management**: Compra y gestión de tickets
- **Payment Management**: Métodos de pago y transacciones (incluye cuenta conjunta)
- **Interaction Management**: Sistema de calificaciones entre usuarios
- **Location Management**: Gestión geográfica
- **Admin Management**: Funciones administrativas

---

## ACTORES DEL SISTEMA

### **ACTOR A001: VISITANTE**

| **Actor** | **Visitante** | **<< A001 >>** |
|-----------|---------------|----------------|
| **Descripción** | Usuario que accede al sistema sin autenticarse y puede realizar consultas públicas |
| **Características** | - No requiere autenticación<br/>- Acceso de solo lectura<br/>- Funciones públicas del sistema |
| **Relaciones** | - Hereda funcionalidades básicas del sistema<br/>- Puede convertirse en Usuario Registrado |
| **Referencias** | - CU-002: Registro de Usuario<br/>- CU-007: Consultar Rifas<br/>- CU-015: Ver Participantes<br/>- CU-020: Ver Calificaciones<br/>- CU-022: Consultar Ubicaciones |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Atributos**
| **Nombre** | **Descripción** | **Tipo** |
|------------|-----------------|----------|
| sesionId | Identificador temporal de sesión | String |
| ipAddress | Dirección IP del visitante | String |
| timestamp | Momento de acceso al sistema | DateTime |

**Listado de los atributos principales del actor, incluyendo su nombre, una pequeña descripción del atributo y su tipo**

#### **Comentarios**
- Actor básico del sistema que representa usuarios no autenticados
- Punto de entrada principal para nuevos usuarios
- Acceso limitado solo a funciones públicas

### **ACTOR A002: USUARIO REGISTRADO**

| **Actor** | **Usuario Registrado** | **<< A002 >>** |
|-----------|------------------------|----------------|
| **Descripción** | Usuario autenticado que puede realizar transacciones y gestionar rifas |
| **Características** | - Requiere autenticación JWT<br/>- Puede crear y participar en rifas<br/>- Gestiona métodos de pago<br/>- Acceso a funciones transaccionales |
| **Relaciones** | - Hereda de Visitante<br/>- Puede ser Organizador de rifas<br/>- Interactúa con otros usuarios |
| **Referencias** | - CU-003: Autenticación Login<br/>- CU-004: Gestión de Perfil<br/>- CU-006: Crear Rifa<br/>- CU-012: Comprar Ticket<br/>- CU-013: Consultar Tickets<br/>- CU-014: Reembolsar Ticket<br/>- CU-016: Estadísticas Usuario<br/>- CU-017: Gestión Métodos de Pago<br/>- CU-018: Verificar Saldo<br/>- CU-019: Calificar Usuario |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Atributos**
| **Nombre** | **Descripción** | **Tipo** |
|------------|-----------------|----------|
| userId | Identificador único del usuario | Integer |
| email | Correo electrónico de autenticación | String |
| firstName | Nombre del usuario | String |
| lastName | Apellido del usuario | String |
| isActive | Estado activo del usuario | Boolean |
| createdAt | Fecha de registro | DateTime |
| lastLogin | Último acceso al sistema | DateTime |

**Listado de los atributos principales del usuario registrado**

#### **Comentarios**
- Actor principal del sistema con capacidades transaccionales
- Puede evolucionar a Organizador al crear rifas
- Gestiona su propio perfil y métodos de pago

### **ACTOR A003: ORGANIZADOR DE RIFAS**

| **Actor** | **Organizador de Rifas** | **<< A003 >>** |
|-----------|---------------------------|----------------|
| **Descripción** | Usuario registrado que ha creado rifas y puede gestionarlas completamente |
| **Características** | - Hereda todas las funciones de Usuario Registrado<br/>- Responsable de rifas creadas<br/>- Puede ejecutar sorteos<br/>- Gestiona cancelaciones |
| **Relaciones** | - Especialización de Usuario Registrado<br/>- Propietario de rifas<br/>- Responsable ante participantes |
| **Referencias** | - CU-008: Actualizar Rifa<br/>- CU-009: Cancelar Rifa<br/>- CU-010: Ejecutar Sorteo<br/>- Hereda todos los CU de Usuario Registrado |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Atributos**
| **Nombre** | **Descripción** | **Tipo** |
|------------|-----------------|----------|
| organizerId | ID único como organizador | Integer |
| totalRaffles | Número total de rifas creadas | Integer |
| activeRaffles | Rifas actualmente activas | Integer |
| completedRaffles | Rifas completadas exitosamente | Integer |
| cancelledRaffles | Rifas canceladas | Integer |
| averageRating | Calificación promedio como organizador | Decimal |

**Listado de los atributos específicos del organizador**

#### **Comentarios**
- Rol especializado que asume responsabilidades legales
- Debe cumplir con las condiciones de sorteo establecidas
- Sujeto a evaluación por parte de los participantes

### **ACTOR A004: ADMINISTRADOR DEL SISTEMA**

| **Actor** | **Administrador del Sistema** | **<< A004 >>** |
|-----------|-------------------------------|----------------|
| **Descripción** | Usuario con permisos administrativos para gestión completa del sistema |
| **Características** | - Máximos privilegios en el sistema<br/>- Puede intervenir en cualquier proceso<br/>- Responsable de mantenimiento y configuración<br/>- Acceso a funciones de auditoría |
| **Relaciones** | - Supervisa todos los actores<br/>- Puede actuar en nombre del sistema<br/>- Responsable de la integridad del sistema |
| **Referencias** | - CU-005: Admin de Usuarios<br/>- CU-011: Cancelación Admin<br/>- CU-021: Admin Ubicaciones<br/>- CU-023: Gestión Catálogos<br/>- Acceso a todos los CU del sistema |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Atributos**
| **Nombre** | **Descripción** | **Tipo** |
|------------|-----------------|----------|
| adminId | Identificador único de administrador | Integer |
| roleLevel | Nivel de permisos administrativos | Integer |
| lastAdminAction | Última acción administrativa | DateTime |
| actionsCount | Número de acciones administrativas | Integer |
| isSuper | Indica si es super administrador | Boolean |
| department | Departamento o área de responsabilidad | String |

**Listado de los atributos específicos del administrador**

#### **Comentarios**
- Rol crítico para la operación del sistema
- Responsable de la seguridad y integridad de datos
- Debe mantener auditoría de todas sus acciones

---

## CASOS DE USO ESPECÍFICOS POR MÓDULO

## 🔐 MÓDULO DE AUTENTICACIÓN Y USUARIOS

### **CU-002: REGISTRO DE USUARIO**

| **Caso de Uso** | Registro de Usuario |
|-----------------|---------------------|
| **ID** | CU-002 |
| **Tipo** | Primario |
| **Referencias** | A001-Visitante |
| **Precondición** | El visitante accede al sistema sin estar autenticado |
| **Postcondición** | Usuario registrado y activo en el sistema |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un visitante se registre en el sistema proporcionando información personal básica para crear una cuenta de usuario.

#### **Resumen**
El visitante completa un formulario de registro con datos personales obligatorios. El sistema valida la información, verifica que no existan duplicados y crea una nueva cuenta de usuario activa.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | El visitante accede al formulario de registro | Sistema muestra formulario con campos obligatorios |
| 2 | Completa datos (email, nombre, apellido, contraseña, ciudad, género, documento) | Sistema recibe información |
| 3 | Envía formulario de registro | Sistema valida formato de datos |
| 4 | | Sistema verifica email único en base de datos |
| 5 | | Sistema verifica documento único |
| 6 | | Sistema hashea contraseña |
| 7 | | Sistema crea usuario con estado activo |
| 8 | | Sistema envía confirmación de registro |
| 9 | Recibe confirmación | Sistema redirige a página de login |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 4A | Email ya existe | Sistema muestra error "Email ya registrado" |
| 5A | Documento ya existe | Sistema muestra error "Documento ya registrado" |
| 3A | Datos incompletos | Sistema muestra campos faltantes |
| 3B | Formato email inválido | Sistema muestra error de formato |

#### **Otros datos**
| **Frecuencia esperada** | Diaria | **Rendimiento** | < 3 segundos |
|-------------------------|--------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Punto de entrada crítico para nuevos usuarios
- Validaciones robustas para evitar duplicados
- Experiencia de usuario fluida y clara

### **CU-003: AUTENTICACIÓN LOGIN**

| **Caso de Uso** | Autenticación Login |
|-----------------|---------------------|
| **ID** | CU-003 |
| **Tipo** | Primario |
| **Referencias** | A002-Usuario Registrado, A003-Organizador, A004-Administrador |
| **Precondición** | Usuario debe estar registrado y activo en el sistema |
| **Postcondición** | Usuario autenticado con tokens JWT válidos |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un usuario registrado acceda al sistema mediante autenticación con credenciales válidas.

#### **Resumen**
El usuario proporciona email y contraseña. El sistema valida las credenciales, genera tokens JWT y establece la sesión autenticada.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a página de login | Sistema muestra formulario de autenticación |
| 2 | Ingresa email y contraseña | Sistema recibe credenciales |
| 3 | Envía formulario de login | Sistema busca usuario por email |
| 4 | | Sistema verifica que usuario esté activo |
| 5 | | Sistema valida contraseña hasheada |
| 6 | | Sistema genera access token JWT (1h) |
| 7 | | Sistema genera refresh token JWT (7d) |
| 8 | | Sistema actualiza último login |
| 9 | | Sistema retorna tokens y datos de usuario |
| 10 | Recibe confirmación de login | Sistema redirige a dashboard |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 3A | Email no existe | Sistema muestra "Credenciales inválidas" |
| 4A | Usuario inactivo | Sistema muestra "Cuenta desactivada" |
| 5A | Contraseña incorrecta | Sistema muestra "Credenciales inválidas" |
| 3B | Campos vacíos | Sistema muestra "Campos obligatorios" |

#### **Otros datos**
| **Frecuencia esperada** | Muy Alta | **Rendimiento** | < 2 segundos |
|-------------------------|----------|-----------------|---------------|
| **Importancia** | Crítica | **Urgencia** | Crítica |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Seguridad mediante JWT con refresh tokens
- No expone información sensible en errores
- Rate limiting para prevenir ataques de fuerza bruta

### **CU-004: GESTIÓN DE PERFIL**

| **Caso de Uso** | Gestión de Perfil |
|-----------------|-------------------|
| **ID** | CU-004 |
| **Tipo** | Secundario |
| **Referencias** | A002-Usuario Registrado, CU-003-Login |
| **Precondición** | Usuario debe estar autenticado en el sistema |
| **Postcondición** | Información personal actualizada en el sistema |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un usuario autenticado consulte y actualice su información personal.

#### **Resumen**
El usuario accede a su área personal para visualizar y modificar sus datos de perfil, incluyendo información personal y configuraciones de cuenta.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a su perfil | Sistema muestra información actual |
| 2 | Visualiza datos personales | Sistema presenta formulario editable |
| 3 | Modifica campos deseados | Sistema valida cambios en tiempo real |
| 4 | Confirma actualización | Sistema valida datos modificados |
| 5 | | Sistema actualiza información |
| 6 | | Sistema confirma cambios guardados |
| 7 | Recibe confirmación | Sistema mantiene sesión activa |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 4A | Email ya existe | Sistema muestra "Email ya registrado por otro usuario" |
| 4B | Datos inválidos | Sistema muestra errores de validación |
| 5A | Error de actualización | Sistema revierte cambios y muestra error |
| CU-004.1 | Cambiar contraseña | Ejecuta subproceso de cambio de contraseña |

#### **Otros datos**
| **Frecuencia esperada** | Media | **Rendimiento** | < 3 segundos |
|-------------------------|-------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Validación en tiempo real para mejor experiencia de usuario
- Mantiene historial de cambios para auditoría
- Opción de desactivar cuenta disponible

### **CU-005: GESTIÓN ADMINISTRATIVA DE USUARIOS**

| **Caso de Uso** | Gestión Administrativa de Usuarios |
|-----------------|-------------------------------------|
| **ID** | CU-005 |
| **Tipo** | Primario |
| **Referencias** | A004-Administrador |
| **Precondición** | Usuario debe tener permisos de administrador |
| **Postcondición** | Cambios aplicados y registrados en auditoría |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un administrador gestione usuarios del sistema con funciones de búsqueda, edición y administración de permisos.

#### **Resumen**
El administrador accede al panel de gestión de usuarios para realizar operaciones administrativas como búsqueda, edición, activación/desactivación y gestión de permisos.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Administrador accede a gestión usuarios | Sistema muestra panel administrativo |
| 2 | Visualiza lista de usuarios | Sistema presenta usuarios paginados |
| 3 | Realiza búsqueda específica | Sistema filtra resultados |
| 4 | Selecciona usuario a gestionar | Sistema muestra detalles del usuario |
| 5 | Realiza cambios necesarios | Sistema valida permisos administrativos |
| 6 | Confirma modificaciones | Sistema aplica cambios |
| 7 | | Sistema registra acción en auditoría |
| 8 | Recibe confirmación | Sistema actualiza vista |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 5A | Sin permisos suficientes | Sistema deniega acción |
| 6A | Usuario tiene rifas activas | Sistema advierte antes de desactivar |
| 7A | Error en auditoría | Sistema rollback de cambios |
| CU-005.1 | Cambiar permisos admin | Requiere confirmación adicional |

#### **Otros datos**
| **Frecuencia esperada** | Baja | **Rendimiento** | < 2 segundos |
|-------------------------|------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Todas las acciones administrativas son auditadas
- Protecciones especiales para usuarios con rifas activas
- Interfaz específica para administradores

---

## 🎲 MÓDULO DE GESTIÓN DE RIFAS

### **CU-006: CREACIÓN DE RIFA**

| **Caso de Uso** | Creación de Rifa |
|-----------------|------------------|
| **ID** | CU-006 |
| **Tipo** | Primario |
| **Referencias** | A002-Usuario Registrado |
| **Precondición** | Usuario autenticado con método de pago válido |
| **Postcondición** | Rifa creada y activa para ventas públicas |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un usuario autenticado cree una nueva rifa definiendo todos los parámetros del sorteo.

#### **Resumen**
El usuario completa un formulario de creación de rifa con parámetros como nombre, fechas, números, precios y premios. El sistema valida la información y activa la rifa para ventas.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a crear rifa | Sistema muestra formulario de creación |
| 2 | Completa nombre y descripción | Sistema valida longitud de campos |
| 3 | Define fecha y hora de sorteo | Sistema valida fecha futura |
| 4 | Establece cantidad total de números | Sistema valida rango permitido |
| 5 | Define precio por número | Sistema valida precio mínimo |
| 6 | Establece mínimo para sortear | Sistema verifica lógica (min ≤ total) |
| 7 | Selecciona tipo y monto de premio | Sistema carga tipos disponibles |
| 8 | Sube imagen opcional | Sistema procesa y optimiza imagen |
| 9 | Confirma creación | Sistema valida todos los parámetros |
| 10 | | Sistema crea rifa en estado "Activo" |
| 11 | | Sistema asigna usuario como organizador |
| 12 | Recibe confirmación | Sistema muestra rifa creada |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 3A | Fecha en el pasado | Sistema muestra "La fecha debe ser futura" |
| 6A | Mínimo > Total | Sistema muestra "Mínimo no puede exceder total" |
| 8A | Imagen muy grande | Sistema comprime automáticamente |
| 9A | Datos inválidos | Sistema muestra errores específicos |

#### **Otros datos**
| **Frecuencia esperada** | Media | **Rendimiento** | < 5 segundos |
|-------------------------|-------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Validaciones complejas para integridad del negocio
- Optimización automática de imágenes
- El usuario se convierte automáticamente en organizador

### **CU-007: CONSULTA PÚBLICA DE RIFAS**

| **Caso de Uso** | Consulta Pública de Rifas |
|-----------------|---------------------------|
| **ID** | CU-007 |
| **Tipo** | Primario |
| **Referencias** | A001-Visitante, A002-Usuario Registrado |
| **Precondición** | Ninguna - Acceso público |
| **Postcondición** | Información de rifas consultada |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Proporcionar acceso público a la información de rifas activas para consulta y participación.

#### **Resumen**
Cualquier visitante puede consultar rifas activas, ver detalles específicos, números disponibles y estadísticas de ventas sin necesidad de autenticación.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Visitante accede a rifas públicas | Sistema muestra lista de rifas activas |
| 2 | Visualiza rifas disponibles | Sistema presenta rifas paginadas |
| 3 | Selecciona rifa específica | Sistema muestra detalles completos |
| 4 | Consulta números disponibles | Sistema actualiza disponibilidad en tiempo real |
| 5 | Visualiza estadísticas | Sistema muestra progreso de ventas |
| 6 | Revisa información del organizador | Sistema presenta perfil público |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 1A | No hay rifas activas | Sistema muestra "No hay rifas disponibles" |
| 3A | Rifa no encontrada | Sistema redirige a lista principal |
| 4A | Todos los números vendidos | Sistema muestra "Agotado" |
| CU-007.1 | Filtrar por organizador | Sistema aplica filtro específico |

#### **Otros datos**
| **Frecuencia esperada** | Muy Alta | **Rendimiento** | < 1 segundo |
|-------------------------|----------|-----------------|---------------|
| **Importancia** | Crítica | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Acceso público sin restricciones
- Cache para optimizar rendimiento
- Actualizaciones en tiempo real de disponibilidad

### **CU-008: ACTUALIZACIÓN DE RIFA**

| **Caso de Uso** | Actualización de Rifa |
|-----------------|----------------------|
| **ID** | CU-008 |
| **Tipo** | Secundario |
| **Referencias** | A003-Organizador de Rifas |
| **Precondición** | Usuario debe ser el organizador de la rifa |
| **Postcondición** | Rifa actualizada con cambios aplicados |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un organizador modifique parámetros específicos de su rifa mientras mantiene la integridad del sistema.

#### **Resumen**
El organizador accede a su rifa para modificar información permitida. El sistema valida los cambios y los aplica manteniendo la consistencia de datos.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Organizador accede a sus rifas | Sistema muestra rifas propias |
| 2 | Selecciona rifa a editar | Sistema verifica propiedad |
| 3 | Accede a edición | Sistema muestra formulario editable |
| 4 | Modifica campos permitidos | Sistema valida cambios en tiempo real |
| 5 | Confirma actualización | Sistema verifica restricciones |
| 6 | | Sistema aplica cambios |
| 7 | | Sistema actualiza timestamps |
| 8 | Recibe confirmación | Sistema muestra rifa actualizada |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | No es el organizador | Sistema deniega acceso |
| 4A | Campo no editable | Sistema muestra "Campo no modificable" |
| 5A | Cambios inválidos | Sistema muestra errores específicos |
| 6A | Rifa ya sorteada | Sistema impide modificaciones |

#### **Otros datos**
| **Frecuencia esperada** | Baja | **Rendimiento** | < 3 segundos |
|-------------------------|------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Restricciones específicas según estado de la rifa
- Solo ciertos campos son editables después de ventas
- Validación de propiedad estricta

### **CU-009: CANCELACIÓN DE RIFA POR ORGANIZADOR**

| **Caso de Uso** | Cancelación de Rifa por Organizador |
|-----------------|-------------------------------------|
| **ID** | CU-009 |
| **Tipo** | Primario |
| **Referencias** | A003-Organizador de Rifas |
| **Precondición** | Rifa no debe estar sorteada y debe pertenecer al organizador |
| **Postcondición** | Rifa cancelada y todos los participantes reembolsados |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un organizador cancele su rifa procesando reembolsos automáticos a todos los participantes.

#### **Resumen**
El organizador solicita cancelación de su rifa. El sistema verifica las condiciones, procesa reembolsos automáticos y cambia el estado de la rifa.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Organizador accede a cancelación | Sistema muestra advertencias |
| 2 | Confirma intención de cancelar | Sistema verifica que no esté sorteada |
| 3 | Proporciona motivo de cancelación | Sistema registra motivo |
| 4 | Confirma cancelación final | Sistema inicia proceso de reembolso |
| 5 | | Sistema obtiene lista de tickets |
| 6 | | Sistema procesa reembolso por cada ticket |
| 7 | | Sistema elimina todos los tickets |
| 8 | | Sistema cambia estado a "Cancelado" |
| 9 | | Sistema registra auditoría completa |
| 10 | | Sistema notifica a participantes |
| 11 | Recibe confirmación | Sistema muestra resumen de cancelación |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | Rifa ya sorteada | Sistema impide cancelación |
| 6A | Error en reembolso | Sistema rollback y notifica error |
| 10A | Error en notificaciones | Sistema continúa pero registra fallo |

#### **Otros datos**
| **Frecuencia esperada** | Muy Baja | **Rendimiento** | < 10 segundos |
|-------------------------|----------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Alta |

#### **Comentarios**
- Proceso irreversible con múltiples confirmaciones
- Transacción atómica para integridad
- Auditoría completa del proceso

### **CU-010: EJECUCIÓN DE SORTEO**

| **Caso de Uso** | Ejecución de Sorteo |
|-----------------|---------------------|
| **ID** | CU-010 |
| **Tipo** | Primario |
| **Referencias** | A003-Organizador de Rifas |
| **Precondición** | Condiciones de sorteo cumplidas (fecha, mínimo vendidos, activa) |
| **Postcondición** | Rifa sorteada con ganador definido y notificado |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un organizador ejecute el sorteo de su rifa cuando se cumplan todas las condiciones necesarias.

#### **Resumen**
El organizador ejecuta el sorteo. El sistema verifica condiciones, selecciona ganador aleatoriamente, actualiza estados y notifica a todos los participantes.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Organizador accede a ejecutar sorteo | Sistema verifica fecha de sorteo |
| 2 | | Sistema verifica mínimo de números vendidos |
| 3 | | Sistema verifica rifa en estado activo |
| 4 | | Sistema verifica no sorteada previamente |
| 5 | | Sistema calcula ganancias/déficit (ingresos - premio) |
| 6 | | Si déficit: Sistema valida saldo del organizador |
| 7 | | Si organizador sin fondos: Sistema cancela y reembolsa automáticamente |
| 8 | Confirma ejecución de sorteo | Sistema obtiene todos los tickets participantes |
| 9 | | Sistema genera número aleatorio criptográfico |
| 10 | | Sistema selecciona ticket ganador |
| 11 | | Sistema inicia transacción |
| 12 | | Si déficit: Organizador transfiere déficit a cuenta conjunta |
| 13 | | Sistema paga premio al ganador desde cuenta conjunta |
| 14 | | Si ganancias positivas: Sistema paga ganancias al organizador desde cuenta conjunta |
| 15 | | Sistema marca ticket como ganador |
| 16 | | Sistema actualiza rifa con datos del ganador |
| 17 | | Sistema cambia estado a "Sorteada" |
| 18 | | Sistema registra auditoría del sorteo |
| 19 | | Sistema confirma transacción |
| 20 | | Sistema notifica al ganador |
| 21 | | Sistema notifica a todos los participantes |
| 22 | Recibe resultados | Sistema muestra datos del ganador |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 1A | Fecha no llegada | Sistema muestra "Aún no es la fecha de sorteo" |
| 2A | Mínimo no alcanzado | Sistema muestra "Mínimo de números no vendidos" |
| 3A | Rifa no activa | Sistema impide sorteo |
| 4A | Ya sorteada | Sistema muestra "Rifa ya sorteada" |
| 6A | Organizador sin saldo para déficit | Sistema cancela rifa automáticamente |
| 6B | Déficit detectado | Sistema reembolsa todos los tickets desde cuenta conjunta |
| 6C | Cancelación por déficit | Sistema cambia estado a "Cancelada" y notifica |
| 11A | Error en transacción | Sistema rollback completo |

#### **Otros datos**
| **Frecuencia esperada** | Baja | **Rendimiento** | < 5 segundos |
|-------------------------|------|-----------------|---------------|
| **Importancia** | Crítica | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Alta |

#### **Comentarios**
- Algoritmo aleatorio criptográficamente seguro
- **Sistema de escrow**: La cuenta conjunta garantiza fondos para premios
- **Validación de déficit**: Si el organizador no puede cubrir la diferencia, la rifa se cancela automáticamente ANTES del sorteo
- **Protección de participantes**: Reembolso automático garantizado si hay problemas
- Proceso auditado completamente
- Notificaciones automáticas a todos los participantes
- El organizador solo recibe ganancias si son positivas; debe cubrir déficits si son negativos

### **CU-011: CANCELACIÓN ADMINISTRATIVA DE RIFA**

| **Caso de Uso** | Cancelación Administrativa de Rifa |
|-----------------|-------------------------------------|
| **ID** | CU-011 |
| **Tipo** | Primario |
| **Referencias** | A004-Administrador del Sistema |
| **Precondición** | Usuario con permisos administrativos |
| **Postcondición** | Rifa cancelada, reembolsos procesados y acción auditada |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un administrador cancele rifas por motivos administrativos, incluyendo casos excepcionales.

#### **Resumen**
El administrador identifica una rifa que debe ser cancelada por motivos administrativos, procesa la cancelación con reembolsos automáticos y registra la acción.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Administrador accede a gestión de rifas | Sistema muestra todas las rifas |
| 2 | Selecciona rifa a cancelar | Sistema muestra detalles de la rifa |
| 3 | Accede a cancelación administrativa | Sistema solicita motivo administrativo |
| 4 | Proporciona motivo detallado | Sistema registra justificación |
| 5 | Confirma cancelación administrativa | Sistema verifica permisos administrativos |
| 6 | | Sistema inicia proceso de reembolso |
| 7 | | Sistema procesa reembolso de todos los tickets |
| 8 | | Sistema cambia estado a "Cancelada-Admin" |
| 9 | | Sistema registra auditoría administrativa |
| 10 | | Sistema notifica al organizador |
| 11 | | Sistema notifica a participantes |
| 12 | Recibe confirmación | Sistema muestra resumen de acción |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 5A | Sin permisos suficientes | Sistema deniega operación |
| 7A | Error en reembolsos | Sistema rollback y registra error |
| CU-011.1 | Rifa ya sorteada | Requiere confirmación especial |

#### **Otros datos**
| **Frecuencia esperada** | Muy Baja | **Rendimiento** | < 15 segundos |
|-------------------------|----------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Variable |
| **Estado** | Implementado | **Complejidad** | Alta |

#### **Comentarios**
- Requiere justificación detallada
- Proceso especial para rifas ya sorteadas
- Auditoría completa de acción administrativa

---

## 🎫 MÓDULO DE GESTIÓN DE TICKETS

### **CU-012: COMPRA DE TICKET**

| **Caso de Uso** | Compra de Ticket |
|-----------------|------------------|
| **ID** | CU-012 |
| **Tipo** | Primario |
| **Referencias** | A002-Usuario Registrado, A003-Organizador |
| **Precondición** | Usuario autenticado, rifa activa, método de pago con saldo |
| **Postcondición** | Ticket comprado, pago procesado, estadísticas actualizadas |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un usuario autenticado compre un número específico en una rifa activa.

#### **Resumen**
El usuario selecciona una rifa activa, elige un número disponible y método de pago. El sistema valida las condiciones, procesa la transacción y crea el ticket.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario navega a rifas activas | Sistema muestra lista de rifas disponibles |
| 2 | Selecciona rifa específica | Sistema muestra detalles y números disponibles |
| 3 | Elige número disponible | Sistema marca número como seleccionado |
| 4 | Selecciona método de pago | Sistema muestra métodos disponibles |
| 5 | Confirma compra | Sistema valida rifa activa |
| 6 | | Sistema verifica número disponible |
| 7 | | Sistema valida saldo suficiente |
| 8 | | Sistema inicia transacción |
| 9 | | Sistema descuenta saldo del método del comprador |
| 10 | | Sistema transfiere dinero a CUENTA CONJUNTA (escrow) |
| 11 | | Sistema crea ticket asociado a la rifa |
| 12 | | Sistema actualiza estadísticas de rifa |
| 13 | | Sistema confirma transacción |
| 14 | | Sistema envía notificación |
| 15 | Recibe confirmación | Sistema muestra ticket comprado |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 5A | Rifa no activa | Sistema muestra "Rifa no disponible para ventas" |
| 6A | Número ya vendido | Sistema actualiza números disponibles |
| 7A | Saldo insuficiente | Sistema muestra "Saldo insuficiente" |
| 8A | Error en transacción | Sistema revierte cambios |

#### **Otros datos**
| **Frecuencia esperada** | Alta | **Rendimiento** | < 5 segundos |
|-------------------------|------|-----------------|---------------|
| **Importancia** | Crítica | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Alta |

#### **Comentarios**
- Transacción atómica para integridad de datos
- **Cuenta conjunta como ESCROW**: El dinero se deposita en una cuenta administrada por el sistema que garantiza fondos para premios y reembolsos
- Validaciones múltiples para evitar conflictos
- Notificaciones inmediatas al usuario
- Protección total de participantes mediante sistema de garantía

### **CU-013: CONSULTA DE TICKETS**

| **Caso de Uso** | Consulta de Tickets |
|-----------------|---------------------|
| **ID** | CU-013 |
| **Tipo** | Secundario |
| **Referencias** | A002-Usuario Registrado |
| **Precondición** | Usuario autenticado en el sistema |
| **Postcondición** | Historial de tickets consultado |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un usuario consulte su historial completo de tickets comprados con filtros y estadísticas.

#### **Resumen**
El usuario accede a su área personal para visualizar todos los tickets comprados, con opciones de filtrado y estadísticas personales.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a sus tickets | Sistema muestra historial completo |
| 2 | Visualiza lista de tickets | Sistema presenta tickets paginados |
| 3 | Aplica filtros si desea | Sistema actualiza resultados |
| 4 | Selecciona ticket específico | Sistema muestra detalles del ticket |
| 5 | Consulta estadísticas | Sistema calcula y muestra métricas |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 1A | Sin tickets comprados | Sistema muestra "No has comprado tickets aún" |
| 3A | Filtro sin resultados | Sistema muestra "No hay tickets con esos criterios" |
| CU-013.1 | Filtrar por rifa | Sistema aplica filtro específico |
| CU-013.2 | Filtrar por estado | Sistema muestra solo tickets activos/ganadores |

#### **Otros datos**
| **Frecuencia esperada** | Alta | **Rendimiento** | < 2 segundos |
|-------------------------|------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Paginación para mejor rendimiento
- Filtros múltiples disponibles
- Estadísticas personales calculadas en tiempo real

### **CU-014: REEMBOLSO DE TICKET**

| **Caso de Uso** | Reembolso de Ticket |
|-----------------|---------------------|
| **ID** | CU-014 |
| **Tipo** | Secundario |
| **Referencias** | A002-Usuario Registrado |
| **Precondición** | Ticket debe pertenecer al usuario y rifa no debe estar sorteada |
| **Postcondición** | Ticket eliminado y dinero reembolsado al método original |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que un usuario reembolse un ticket individual antes del sorteo, recuperando su dinero.

#### **Resumen**
El usuario selecciona un ticket propio para reembolsar. El sistema valida las condiciones, procesa el reembolso y elimina el ticket.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a sus tickets | Sistema muestra tickets reembolsables |
| 2 | Selecciona ticket específico | Sistema verifica propiedad del ticket |
| 3 | Solicita reembolso | Sistema valida que rifa no esté sorteada |
| 4 | Confirma reembolso | Sistema inicia proceso de reembolso |
| 5 | | Sistema identifica método de pago original |
| 6 | | Sistema procesa devolución de dinero |
| 7 | | Sistema elimina ticket |
| 8 | | Sistema actualiza estadísticas de rifa |
| 9 | | Sistema registra transacción de reembolso |
| 10 | Recibe confirmación | Sistema muestra comprobante |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | Ticket no pertenece al usuario | Sistema deniega acceso |
| 3A | Rifa ya sorteada | Sistema impide reembolso |
| 6A | Error en reembolso | Sistema rollback y notifica error |
| 5A | Método de pago inactivo | Sistema contacta soporte |

#### **Otros datos**
| **Frecuencia esperada** | Baja | **Rendimiento** | < 5 segundos |
|-------------------------|------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Solo disponible antes del sorteo
- Reembolso al método de pago original
- Actualiza automáticamente estadísticas de rifa

### **CU-015: CONSULTA PÚBLICA DE TICKETS DE RIFA**

| **Caso de Uso** | Consulta Pública de Tickets de Rifa |
|-----------------|--------------------------------------|
| **ID** | CU-015 |
| **Tipo** | Secundario |
| **Referencias** | A001-Visitante, A002-Usuario Registrado |
| **Precondición** | Ninguna - Acceso público |
| **Postcondición** | Información de participantes consultada |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Proporcionar transparencia pública mostrando todos los participantes de una rifa específica.

#### **Resumen**
Cualquier visitante puede consultar qué números están ocupados en una rifa y ver información pública de los participantes.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Visitante accede a rifa específica | Sistema muestra detalles de la rifa |
| 2 | Selecciona ver participantes | Sistema muestra todos los tickets vendidos |
| 3 | Visualiza números ocupados | Sistema presenta grid de números |
| 4 | Consulta información de participantes | Sistema muestra datos públicos |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | Sin tickets vendidos | Sistema muestra "Aún no hay participantes" |
| 4A | Participante privado | Sistema oculta información personal |

#### **Otros datos**
| **Frecuencia esperada** | Media | **Rendimiento** | < 2 segundos |
|-------------------------|-------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Baja |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Transparencia total del proceso
- Respeta privacidad de usuarios
- Información actualizada en tiempo real

### **CU-016: ESTADÍSTICAS DE USUARIO**

| **Caso de Uso** | Estadísticas de Usuario |
|-----------------|-------------------------|
| **ID** | CU-016 |
| **Tipo** | Secundario |
| **Referencias** | A002-Usuario Registrado |
| **Precondición** | Usuario autenticado en el sistema |
| **Postcondición** | Estadísticas personales calculadas y mostradas |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Proporcionar al usuario un resumen estadístico completo de su participación en el sistema.

#### **Resumen**
El usuario accede a su dashboard personal para visualizar métricas detalladas de su actividad en rifas.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a estadísticas | Sistema calcula métricas personales |
| 2 | Visualiza dashboard | Sistema muestra total de tickets comprados |
| 3 | | Sistema muestra tickets ganadores |
| 4 | | Sistema muestra tickets activos |
| 5 | | Sistema calcula dinero total gastado |
| 6 | | Sistema calcula tasa de éxito |
| 7 | | Sistema presenta gráficos y tendencias |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 1A | Usuario sin actividad | Sistema muestra "Aún no has participado en rifas" |
| 7A | Datos insuficientes para gráficos | Sistema muestra solo números básicos |

#### **Otros datos**
| **Frecuencia esperada** | Media | **Rendimiento** | < 3 segundos |
|-------------------------|-------|-----------------|---------------|
| **Importancia** | Baja | **Urgencia** | Baja |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Cálculos en tiempo real
- Gráficos interactivos cuando hay suficientes datos
- Historiales de tendencias de participación

---

## 💳 MÓDULO DE MÉTODOS DE PAGO

### **CU-017: GESTIÓN DE MÉTODOS DE PAGO**

| **Caso de Uso** | Gestión de Métodos de Pago |
|-----------------|----------------------------|
| **ID** | CU-017 |
| **Tipo** | Primario |
| **Referencias** | A002-Usuario Registrado |
| **Precondición** | Usuario autenticado en el sistema |
| **Postcondición** | Métodos de pago registrados y gestionados |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que el usuario gestione completamente sus métodos de pago para realizar transacciones en el sistema.

#### **Resumen**
El usuario puede agregar, consultar, verificar y gestionar sus métodos de pago de forma segura con información hasheada.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a métodos de pago | Sistema muestra métodos registrados |
| 2 | Selecciona agregar nuevo método | Sistema muestra formulario seguro |
| 3 | Completa información de tarjeta | Sistema valida formato en tiempo real |
| 4 | Confirma registro | Sistema hashea número de tarjeta |
| 5 | | Sistema registra método de pago |
| 6 | | Sistema confirma registro exitoso |
| 7 | Consulta métodos disponibles | Sistema muestra lista con información hasheada |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 3A | Tarjeta inválida | Sistema muestra errores de validación |
| 4A | Tarjeta ya registrada | Sistema muestra "Método ya existe" |
| CU-017.1 | Desactivar método | Requiere confirmación adicional |
| CU-017.2 | Verificar saldo | Sistema consulta disponibilidad |

#### **Otros datos**
| **Frecuencia esperada** | Baja | **Rendimiento** | < 3 segundos |
|------------------------|------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Alta |
| **Estado** | Implementado | **Complejidad** | Alta |

#### **Comentarios**
- Información sensible siempre hasheada
- Validaciones robustas de seguridad
- Nunca se almacenan números de tarjeta completos

### **CU-018: VERIFICACIÓN DE SALDO**

| **Caso de Uso** | Verificación de Saldo |
|-----------------|----------------------|
| **ID** | CU-018 |
| **Tipo** | Secundario |
| **Referencias** | A002-Usuario Registrado, CU-017 |
| **Precondición** | Usuario autenticado con métodos de pago registrados |
| **Postcondición** | Disponibilidad de fondos verificada |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir al usuario verificar la disponibilidad de fondos antes de realizar una compra.

#### **Resumen**
El usuario puede consultar si tiene saldo suficiente en sus métodos de pago para proceder con transacciones sin exponer información sensible.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario inicia compra de ticket | Sistema identifica precio total |
| 2 | Selecciona método de pago | Sistema valida propiedad del método |
| 3 | Solicita verificación de saldo | Sistema consulta disponibilidad |
| 4 | | Sistema retorna estado: suficiente/insuficiente |
| 5 | | Sistema habilita/deshabilita botón comprar |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | Método no válido | Sistema muestra "Método inválido" |
| 4A | Saldo insuficiente | Sistema sugiere otros métodos |
| 4B | Error de consulta | Sistema permite reintentar |
| CU-018.1 | Consulta manual | Usuario puede verificar antes de comprar |

#### **Otros datos**
| **Frecuencia esperada** | Alta | **Rendimiento** | < 2 segundos |
|------------------------|------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Por seguridad no se expone el saldo exacto
- Solo se informa si es suficiente o no
- Validación antes de cada transacción

---

## ⭐ MÓDULO DE INTERACCIONES Y CALIFICACIONES

### **CU-019: CALIFICACIÓN DE USUARIO**

| **Caso de Uso** | Calificación de Usuario |
|-----------------|------------------------|
| **ID** | CU-019 |
| **Tipo** | Secundario |
| **Referencias** | A002-Usuario Registrado, CU-012 |
| **Precondición** | Usuario autenticado con interacciones previas |
| **Postcondición** | Calificación registrada y promedio actualizado |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir que los usuarios califiquen a otros usuarios después de interacciones comerciales para construir reputación.

#### **Resumen**
Los usuarios pueden otorgar calificaciones de 1 a 5 estrellas con comentarios opcionales, validando unicidad y actualizando automáticamente promedios.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a perfil del organizador | Sistema muestra opción "Calificar" |
| 2 | Selecciona calificar usuario | Sistema valida no haya calificación previa |
| 3 | Asigna estrellas (1-5) | Sistema registra puntuación |
| 4 | Agrega comentario (opcional) | Sistema valida contenido |
| 5 | Confirma calificación | Sistema guarda en base datos |
| 6 | | Sistema recalcula promedio automáticamente |
| 7 | | Sistema notifica usuario calificado |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | Ya existe calificación | Sistema muestra "Ya calificaste a este usuario" |
| 4A | Comentario inapropiado | Sistema rechaza y solicita revisión |
| CU-019.1 | Modificar calificación | Sistema permite actualizar una vez |
| CU-019.2 | Ver mis calificaciones | Muestra historial de calificaciones dadas |

#### **Otros datos**
| **Frecuencia esperada** | Media | **Rendimiento** | < 2 segundos |
|------------------------|--------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Solo una calificación activa por par de usuarios
- El promedio se actualiza mediante signals de Django
- Las calificaciones son públicas y permanentes

### **CU-020: CONSULTA DE CALIFICACIONES**

| **Caso de Uso** | Consulta de Calificaciones |
|-----------------|---------------------------|
| **ID** | CU-020 |
| **Tipo** | Primario |
| **Referencias** | A001-Visitante, A002-Usuario Registrado |
| **Precondición** | Ninguna (acceso público) |
| **Postcondición** | Calificaciones y reputación mostradas |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Proporcionar transparencia y confianza mostrando públicamente las calificaciones y reputación de los usuarios.

#### **Resumen**
Cualquier visitante puede consultar las calificaciones, comentarios y estadísticas de reputación de cualquier usuario del sistema.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Visitante accede a perfil público | Sistema muestra información básica |
| 2 | Consulta sección calificaciones | Sistema muestra promedio con estrellas |
| 3 | | Sistema lista comentarios públicos |
| 4 | | Sistema muestra estadísticas (total calificaciones) |
| 5 | Filtra por usuario calificador | Sistema aplica filtros seleccionados |
| 6 | | Sistema actualiza vista con datos filtrados |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 2A | Usuario sin calificaciones | Sistema muestra "Sin calificaciones aún" |
| 5A | Sin datos en filtro | Sistema muestra mensaje informativo |
| CU-020.1 | Ordenar por fecha | Sistema reordena comentarios |
| CU-020.2 | Ver solo calificaciones altas | Sistema filtra 4-5 estrellas |

#### **Otros datos**
| **Frecuencia esperada** | Alta | **Rendimiento** | < 2 segundos |
|------------------------|------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Información completamente pública
- Fomenta la transparencia y confianza
- Los comentarios ofensivos pueden ser reportados

---

## 🌍 MÓDULO DE GESTIÓN GEOGRÁFICA

### **CU-021: GESTIÓN DE UBICACIONES**

| **Caso de Uso** | Gestión de Ubicaciones |
|-----------------|----------------------|
| **ID** | CU-021 |
| **Tipo** | Secundario |
| **Referencias** | A004-Administrador |
| **Precondición** | Usuario con permisos administrativos |
| **Postcondición** | Estructura geográfica actualizada |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir al administrador gestionar la estructurar geográfica jerárquica del sistema (países, estados, ciudades).

#### **Resumen**
El administrador puede crear, modificar, activar y desactivar elementos geográficos manteniendo la integridad jerárquica del sistema.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Administrador accede a gestión geográfica | Sistema muestra panel administrativo |
| 2 | Selecciona nivel geográfico (país/estado/ciudad) | Sistema muestra lista actual |
| 3 | Crea nuevo elemento | Sistema valida datos obligatorios |
| 4 | Completa información requerida | Sistema valida unicidad |
| 5 | Confirma creación | Sistema registra en jerarquía |
| 6 | | Sistema actualiza dependencias |
| 7 | | Sistema confirma operación exitosa |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 3A | Modificar existente | Sistema carga datos actuales |
| 4A | Nombre duplicado | Sistema rechaza y solicita nombre único |
| CU-021.1 | Desactivar ubicación | Sistema valida que no esté en uso |
| CU-021.2 | Activar ubicación | Sistema habilita para uso |

#### **Otros datos**
| **Frecuencia esperada** | Muy Baja | **Rendimiento** | < 3 segundos |
|------------------------|-----------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Baja |
| **Estado** | Implementado | **Complejidad** | Media |

#### **Comentarios**
- Mantiene integridad referencial jerárquica
- No se pueden eliminar ubicaciones con datos asociados
- Soft delete para preservar historial

### **CU-022: CONSULTA PÚBLICA DE UBICACIONES**

| **Caso de Uso** | Consulta Pública de Ubicaciones |
|-----------------|--------------------------------|
| **ID** | CU-022 |
| **Tipo** | Primario |
| **Referencias** | A001-Visitante, A002-Usuario Registrado, A003-Organizador |
| **Precondición** | Ninguna (acceso público) |
| **Postcondición** | Ubicaciones geográficas consultadas |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Proporcionar acceso público a la estructura geográfica para completar formularios y filtrar información.

#### **Resumen**
Cualquier usuario puede consultar países, estados y ciudades activos de forma jerárquica para seleccionar ubicaciones.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Usuario accede a selector de ubicación | Sistema muestra países activos |
| 2 | Selecciona país | Sistema carga estados del país |
| 3 | Selecciona estado | Sistema carga ciudades del estado |
| 4 | Selecciona ciudad | Sistema registra selección completa |
| 5 | | Sistema habilita campos dependientes |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 1A | Búsqueda por texto | Sistema filtra ubicaciones que coincidan |
| 2A | País sin estados | Sistema muestra mensaje informativo |
| 3A | Estado sin ciudades | Sistema permite continuar sin ciudad |
| CU-022.1 | Búsqueca rápida | Sistema sugiere ubicaciones mientras escribe |

#### **Otros datos**
| **Frecuencia esperada** | Alta | **Rendimiento** | < 1 segundo |
|------------------------|------|-----------------|---------------|
| **Importancia** | Alta | **Urgencia** | Media |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Solo muestra ubicaciones activas
- Carga jerárquica para mejor experiencia
- Soporte para autocompletado y búsqueda

---

## 📊 MÓDULO DE INFORMACIÓN CATALOGADA

### CU-023: Gestión de Catálogos
**Actor**: Administrador
**Descripción**: Administrador gestiona información catalogada del sistema.

| **Caso de Uso** | Gestión de Catálogos |
|-----------------|---------------------|
| **ID** | CU-023 |
| **Tipo** | Secundario |
| **Referencias** | A004-Administrador |
| **Precondición** | Usuario con permisos administrativos |
| **Postcondición** | Catálogos del sistema actualizados |

| **Autor** | Sistema de Rifas | **Fecha** | 10/11/2025 | **Versión** | 1.0 |
|-----------|------------------|-----------|------------|-------------|-----|

#### **Propósito**
Permitir al administrador gestionar la información catalogada que utiliza el sistema para mantener consistencia de datos.

#### **Resumen**
El administrador puede crear, modificar y gestionar catálogos de tipos de documento, géneros, tipos de premio, estados de rifa y tipos de métodos de pago.

#### **Curso Normal**
| **Paso** | **Acción del Actor** | **Respuesta del Sistema** |
|----------|---------------------|---------------------------|
| 1 | Administrador accede a gestión catálogos | Sistema muestra catálogos disponibles |
| 2 | Selecciona catálogo específico | Sistema muestra elementos actuales |
| 3 | Crea nuevo elemento | Sistema valida datos obligatorios |
| 4 | Completa información requerida | Sistema valida unicidad del nombre |
| 5 | Confirma creación | Sistema registra nuevo elemento |
| 6 | | Sistema actualiza cache del catálogo |
| 7 | | Sistema confirma operación exitosa |

#### **Cursos Alternos**
| **Paso** | **Condición** | **Acción** |
|----------|---------------|------------|
| 3A | Modificar elemento existente | Sistema carga datos actuales para edición |
| 4A | Nombre duplicado | Sistema rechaza y solicita nombre único |
| CU-023.1 | Activar/desactivar elemento | Sistema cambia estado sin eliminar |
| CU-023.2 | Ordenar elementos | Sistema permite cambiar orden de visualización |

#### **Otros datos**
| **Frecuencia esperada** | Muy Baja | **Rendimiento** | < 2 segundos |
|------------------------|-----------|-----------------|---------------|
| **Importancia** | Media | **Urgencia** | Baja |
| **Estado** | Implementado | **Complejidad** | Baja |

#### **Comentarios**
- Los elementos no se eliminan, solo se desactivan
- Cambios requieren actualización de cache
- Mantiene integridad referencial con datos existentes

---

## MATRIZ DE CASOS DE USO POR ACTOR

| Caso de Uso | Visitante | Usuario | Organizador | Admin | Descripción |
|-------------|-----------|---------|-------------|-------|-------------|
| CU-002 | ✅ | - | - | - | Registro de Usuario |
| CU-003 | - | ✅ | ✅ | ✅ | Autenticación Login |
| CU-004 | - | ✅ | ✅ | ✅ | Gestión de Perfil |
| CU-005 | - | - | - | ✅ | Admin de Usuarios |
| CU-006 | - | ✅ | ✅ | ✅ | Crear Rifa |
| CU-007 | ✅ | ✅ | ✅ | ✅ | Consultar Rifas |
| CU-008 | - | - | ✅ | ✅ | Actualizar Rifa |
| CU-009 | - | - | ✅ | ✅ | Cancelar Rifa |
| CU-010 | - | - | ✅ | ✅ | Ejecutar Sorteo |
| CU-011 | - | - | - | ✅ | Cancelación Admin |
| CU-012 | - | ✅ | ✅ | ✅ | Comprar Ticket |
| CU-013 | - | ✅ | ✅ | ✅ | Consultar Tickets |
| CU-014 | - | ✅ | ✅ | ✅ | Reembolsar Ticket |
| CU-015 | ✅ | ✅ | ✅ | ✅ | Ver Participantes |
| CU-016 | - | ✅ | ✅ | ✅ | Estadísticas Usuario |
| CU-017 | - | ✅ | ✅ | ✅ | Gestión Métodos Pago |
| CU-018 | - | ✅ | ✅ | ✅ | Verificar Saldo |
| CU-019 | - | ✅ | ✅ | ✅ | Calificar Usuario |
| CU-020 | ✅ | ✅ | ✅ | ✅ | Ver Calificaciones |
| CU-021 | - | - | - | ✅ | Admin Ubicaciones |
| CU-022 | ✅ | ✅ | ✅ | ✅ | Consultar Ubicaciones |
| CU-023 | - | - | - | ✅ | Gestión Catálogos |

---

## PATRONES DE DISEÑO IDENTIFICADOS

### 1. **Repository Pattern**
- Cada modelo actúa como repositorio de datos
- Métodos especializados para operaciones complejas
- Separación entre lógica de negocio y acceso a datos

### 2. **Factory Pattern**
- Creación de usuarios con `CustomUserManager`
- Generación automática de paths para imágenes
- Asignación automática de estados por defecto

### 3. **Strategy Pattern**
- Diferentes tipos de métodos de pago
- Múltiples estados de rifa con comportamientos específicos
- Validaciones contextuales según el estado

### 4. **Observer Pattern**
- Signals de Django para actualizar calificaciones automáticamente
- Actualización automática de estadísticas de rifa

### 5. **Command Pattern**
- Operaciones complejas encapsuladas en métodos del modelo
- `execute_raffle_draw()`, `soft_delete_and_refund()`, etc.

### 6. **MVC Pattern**
- Separación clara entre Models, Views y Serializers
- Controllers implícitos en ViewSets de Django REST

### 7. **Decorator Pattern**
- Permisos customizados como decoradores
- Validaciones de middleware JWT

---

## CONSIDERACIONES TÉCNICAS

### Seguridad Implementada:
- Autenticación JWT con refresh tokens
- Hashing de números de tarjeta
- Validaciones de propiedad en todas las operaciones
- Permisos granulares por endpoint

### Integridad de Datos:
- Transacciones atómicas para operaciones críticas
- Constraints de base de datos
- Validaciones a nivel de modelo y serializer

### Escalabilidad:
- Índices estratégicos en modelos
- Queries optimizadas con select_related
- Paginación en endpoints de listado

### Auditabilidad:
- Timestamps automáticos en todas las entidades
- Registro de motivos en cancelaciones administrativas
- Historial completo de transacciones

---

## MÉTRICAS DEL SISTEMA

### 📈 **Estadísticas Generales:**
- **Total de Casos de Uso Identificados**: 23
- **Módulos del Sistema**: 7
- **Actores del Sistema**: 4 (Visitante, Usuario, Organizador, Administrador)
- **Endpoints de API**: ~50
- **Modelos de Datos**: 12
- **Relaciones entre Modelos**: 18+

### 📊 **Distribución por Módulo:**
- **Autenticación y Usuarios**: 4 casos de uso
- **Gestión de Rifas**: 6 casos de uso
- **Gestión de Tickets**: 5 casos de uso
- **Métodos de Pago**: 2 casos de uso
- **Interacciones**: 2 casos de uso
- **Gestión Geográfica**: 2 casos de uso
- **Información Catalogada**: 1 caso de uso
- **Administración**: 1 caso de uso

### 🎯 **Complejidad del Sistema:**
- **Casos de Uso por Actor**:
  - Visitante: 5 casos de uso
  - Usuario: 14 casos de uso
  - Organizador: 17 casos de uso (incluye Usuario)
  - Administrador: 19 casos de uso (incluye funciones especiales)

### 🔒 **Aspectos de Seguridad Cubiertos:**
- Autenticación JWT con refresh tokens
- Validaciones de propiedad en operaciones
- Hashing de datos sensibles (tarjetas)
- Auditoría completa de transacciones
- Permisos granulares por endpoint
- Transacciones atómicas para integridad

---

## 📝 **NOTAS TÉCNICAS**

### **Tecnologías Base:**
- **Backend**: Django 5.2.6 + Django REST Framework
- **Base de Datos**: MySQL
- **Cache**: Redis (recomendado para producción)
- **Autenticación**: JWT (SimpleJWT)
- **Archivos**: Sistema de archivos local + CDN (recomendado)

### **Consideraciones de Escalabilidad:**
- Índices estratégicos en modelos críticos
- Queries optimizadas con select_related/prefetch_related
- Paginación en todos los endpoints de listado
- Cache de consultas frecuentes (Redis)
- CDN para imágenes de rifas

### **Auditoría y Logging:**
- Timestamps automáticos en todas las entidades
- Log completo de operaciones administrativas
- Registro de motivos en cancelaciones
- Trazabilidad de transacciones financieras
- Historial completo de cambios de estado

---

*📅 Documento generado el 10 de noviembre de 2025*  
*🎲 Sistema: Rifas Online v1.0*  
*🛠️ Framework: Django REST Framework*  
*📄 Total de Casos de Uso: 23 casos de uso identificados y documentados*