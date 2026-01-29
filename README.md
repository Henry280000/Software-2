# E-Commerce - MySQL + MongoDB + Docker

Sistema de comercio electrónico con arquitectura híbrida de bases de datos.

## Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/Henry280000/Ordinario_Data_Bases.git
cd Ordinario_Data_Bases

# 2. Levantar el sistema con Docker
docker-compose up -d

# 3. Esperar a que las bases de datos estén listas (30 segundos)
sleep 30

# 4. Acceder: http://localhost:5001
```

## Credenciales de Acceso

**Usuarios Pre-configurados:**

| Rol | Email | Contraseña | Descripción |
|-----|-------|------------|-------------|
| ADMIN | admin@jerseys.com | password123 | Acceso completo al sistema |
| CLIENTE | juan@email.com | password123 | Usuario de prueba 1 |
| CLIENTE | maria@email.com | password123 | Usuario de prueba 2 |

**Nota:** Todos los usuarios usan la misma contraseña: `password123`

## Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────┐
│  Frontend: HTML5 + CSS3 + JavaScript (minimal)      │
│  Backend: Python 3.11 + Flask 3.0 + Jinja2         │
│  ├── MySQL 8.0: Transacciones ACID                  │
│  │   ├── Usuarios (3 usuarios + registros)         │
│  │   ├── Pedidos (órdenes de compra)               │
│  │   ├── DetallePedido (items por pedido)          │
│  │   └── Inventario (36 SKUs: 9 equipos × 4 tallas)│
│  └── MongoDB 6.0: Catálogo NoSQL                    │
│      ├── jerseys (9 productos activos)             │
│      ├── comentarios (reseñas de productos)        │
│      └── logs (auditoría del sistema)              │
└──────────────────────────────────────────────────────┘
```

## Catálogo de Productos

**9 Equipos Disponibles:**
- Barcelona (España)
- Real Madrid (España)
- Manchester United (Inglaterra)
- Liverpool (Inglaterra)
- PSG (Francia)
- Bayern Munich (Alemania)
- Club América (México)
- Borussia Dortmund (Alemania)
- Inter Miami (USA)

**Tallas:** S, M, L, XL (4 tallas por equipo = 36 SKUs totales)  
**Precios:** $79.99 - $89.99 USD

## Estructura del Proyecto

```
ordinario/
├── backend/
│   ├── app_new.py              # Aplicación principal (SE USA)         
│   ├── templates/              # Templates Jinja2 (11 archivos)
│   ├── static/
│   │   ├── css/
│   │   │   └── modern-styles.css
│   │   ├── js/
│   │   │   └── ux-enhancements.js
│   │   └── archivos_antiguos/  # JS/HTML obsoletos
│   ├── db_mysql.py
│   ├── db_mongodb.py
│   ├── .env
│   └── requirements.txt
├── database/
│   ├── mysql/                  # Scripts SQL iniciales
│   └── mongodb/                # Scripts JS iniciales
├── scripts/
│   └── sync_inventory.py       # Sincronización MongoDB → MySQL
├── docker-compose.yml
└── venv/                       # Entorno virtual Python
```

## Funcionalidades Implementadas

### Públicas (Sin Login)
- Página de inicio con información del sistema
- Catálogo completo de 9 jerseys
- Búsqueda de productos por nombre/equipo
- Ver detalles completos de cada jersey
- Agregar productos al carrito (guardado en sesión)
- Gestionar carrito: aumentar/disminuir cantidades, eliminar items
- Registro de nuevos usuarios

### Usuarios Registrados (CLIENTE)
- Login/Logout con sesiones Flask
- Realizar compras con validación de stock
- Formulario de checkout con búsqueda de código postal
- Ver historial completo de pedidos
- Ver detalles de cada pedido (productos, precios, estado)
- Carrito persistente durante la sesión

### Administradores (ADMIN)
- Dashboard con estadísticas del sistema:
  * Total de clientes
  * Total de pedidos
  * Ingresos totales
  * Pedidos pendientes
- Gestión completa de pedidos:
  * Ver todos los pedidos
  * Filtrar por estado (PENDIENTE, PROCESANDO, COMPLETADO, CANCELADO)
  * Cambiar estado de pedidos
- Gestión de inventario:
  * Ver stock de todos los productos (36 SKUs)
  * Actualizar cantidades disponibles
  * Agregar nuevos productos al inventario
  * Indicadores visuales de stock (bajo/medio/alto)

## Comandos Útiles

### Docker - Gestión de Contenedores
```bash
# Ver logs del backend en tiempo real
docker logs backend_ecommerce -f

# Ver estado de todos los contenedores
docker ps

# Reiniciar un servicio específico
docker-compose restart backend

# Detener todos los servicios
docker-compose down

# Resetear TODO (elimina volúmenes y datos)
docker-compose down -v
docker-compose up -d
```

### MySQL - Consultas Directas
```bash
# Conectar a MySQL interactivo
docker exec -it mysql_ecommerce mysql -u root -prootpassword ecommerce_db

# Ver todos los usuarios
docker exec mysql_ecommerce mysql -u root -prootpassword -e "SELECT id_usuario, nombre, email, rol FROM Usuarios;" ecommerce_db

# Ver inventario completo (36 SKUs)
docker exec mysql_ecommerce mysql -u root -prootpassword -e "SELECT sku, nombre_producto, talla, cantidad_disponible, precio_unitario FROM Inventario ORDER BY nombre_producto, talla;" ecommerce_db

# Ver pedidos
docker exec mysql_ecommerce mysql -u root -prootpassword -e "SELECT id_pedido, id_usuario, fecha_pedido, total, estado FROM Pedidos ORDER BY fecha_pedido DESC;" ecommerce_db

# Resetear inventario a valores iniciales
docker exec mysql_ecommerce mysql -u root -prootpassword -e "UPDATE Inventario SET cantidad_disponible = 50 WHERE cantidad_disponible < 10;" ecommerce_db
```

### MongoDB - Consultas Directas
```bash
# Conectar a MongoDB interactivo
docker exec -it mongodb_ecommerce mongosh -u admin -p adminpassword --authenticationDatabase admin

# Ver todos los jerseys
docker exec mongodb_ecommerce mongosh -u admin -p adminpassword --authenticationDatabase admin --eval "db.getSiblingDB('ecommerce_catalog').jerseys.find({}, {nombre: 1, equipo: 1, precio_base: 1}).pretty()"

# Contar productos activos
docker exec mongodb_ecommerce mongosh -u admin -p adminpassword --authenticationDatabase admin --eval "db.getSiblingDB('ecommerce_catalog').jerseys.countDocuments({activo: true})"

# Ver un producto específico
docker exec mongodb_ecommerce mongosh -u admin -p adminpassword --authenticationDatabase admin --eval "db.getSiblingDB('ecommerce_catalog').jerseys.findOne({_id: 'jersey_rm_home_2024'})"
```

## Desarrollo Local (Sin Docker para Backend)

```bash
# 1. Levantar solo las bases de datos
docker-compose up -d mysql_db mongodb_db

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Ejecutar backend
cd backend
python app_new.py

# 4. Acceder: http://localhost:5001
```

## Tecnologías

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Backend | Python | 3.11 |
| Framework | Flask | 3.0.0 |
| Templates | Jinja2 | 3.1.6 |
| BD Relacional | MySQL | 8.0 |
| BD NoSQL | MongoDB | 6.0 |
| Orquestación | Docker Compose | 3.8 |
| Seguridad | bcrypt | 4.1.1 |
| Frontend | HTML5 + CSS3 + JS | - |

## Esquema de Base de Datos

### MySQL 8.0 (Transaccional - ACID)

**Tabla: Usuarios**
```sql
id_usuario (PK), nombre, email (UNIQUE), password_hash, 
rol (ADMIN/CLIENTE), fecha_registro, activo
```

**Tabla: Inventario**
```sql
id_inventario (PK), sku (UNIQUE), producto_id, nombre_producto,
talla, cantidad_disponible, precio_unitario, fecha_actualizacion
```

**Tabla: Pedidos**
```sql
id_pedido (PK), id_usuario (FK), fecha_pedido, total,
estado (PENDIENTE/PROCESANDO/COMPLETADO/CANCELADO),
direccion_envio, notas
```

**Tabla: DetallePedido**
```sql
id_detalle (PK), id_pedido (FK), sku (FK), nombre_producto,
talla, cantidad, precio_unitario, subtotal
```

**Stored Procedures:**
- `sp_crear_pedido`: Crea pedido con transacción atómica
- `sp_actualizar_stock`: Actualiza inventario con bloqueo

### MongoDB 6.0 (Catálogo NoSQL)

**Colección: jerseys**
```javascript
{
  _id: "jersey_rm_home_2024",
  nombre: "Real Madrid Jersey Home 2024",
  equipo: "Real Madrid",
  marca: "Adidas",
  temporada: "2024/2025",
  tipo: "Home",
  descripcion: "...",
  categoria: "Clubes Europeos",
  tallas_disponibles: ["S", "M", "L", "XL", "XXL"],
  precio_base: 89.99,
  activo: true,
  tags: ["real madrid", "adidas", "la liga"]
}
```

**Índices en MongoDB:**
- marca, equipo, temporada, precio_base, categoria, tags

## Seguridad Implementada

- Contraseñas hasheadas con bcrypt (costo 12)
- Sesiones del lado del servidor con Flask Sessions
- Secret key para firmar cookies de sesión
- Validación de roles en decoradores (@admin_required, @login_required)
- Prepared statements en todas las queries SQL (previene SQL injection)
- Validación de entrada en formularios (servidor y cliente)
- Transacciones ACID con rollback automático en errores
- Bloqueo de filas (FOR UPDATE) en actualizaciones de inventario
- Control de acceso basado en roles (RBAC en aplicación)

## Solución de Problemas

### Backend no arranca
```bash
docker logs backend_ecommerce
docker-compose restart backend
```

### No aparecen productos
```bash
docker exec backend_ecommerce python /app/scripts/sync_inventory.py
```

### No puedo hacer login
```bash
# Verificar usuarios
docker exec mysql_ecommerce mysql -u ecommerce_user -pecommerce_pass -e "SELECT * FROM Usuarios;" ecommerce_db
# Si no hay usuarios, regístrate en /register
```

### CSS no carga
```bash
# Verificar archivo existe
docker exec backend_ecommerce ls -la /app/static/css/
docker-compose restart backend
```

## Variables de Entorno

El sistema usa las siguientes variables (archivo `.env`):

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=rootpassword
MYSQL_DATABASE=ecommerce_db

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USER=admin
MONGODB_PASSWORD=adminpassword
MONGODB_DATABASE=ecommerce_catalog

# Flask Configuration
SECRET_KEY=tu_clave_secreta_muy_segura_cambiala_12345
FLASK_ENV=development
```

## Notas Importantes

- **JavaScript es OPCIONAL:** Toda la funcionalidad principal funciona sin JavaScript
- **Server-Side Rendering:** Todo se renderiza en el servidor con Jinja2 (más rápido y seguro)
- **Auto-open Browser:** El servidor abre automáticamente el navegador al iniciar
- **Sin Frontend Separado:** No se usa React, Vue, ni Angular (simplicidad)
- **Código Limpio:** Sin comentarios decorativos ni emojis en el código
- **Git Ignore:** Carpeta `frontend/` y archivos `.md` obsoletos están ignorados

## Características Técnicas Destacadas

**Backend:**
- Flask con blueprints implícitos (funciones decoradas)
- Jinja2 templates con herencia y bloques
- Sesiones del lado del servidor
- Decoradores personalizados para autorización
- Manejo de errores con try/except y transacciones

**Base de Datos:**
- MySQL con stored procedures y transacciones ACID
- MongoDB con índices optimizados para búsquedas
- Arquitectura híbrida: transaccional + NoSQL
- 36 SKUs con control de stock en tiempo real

**Docker:**
- 3 contenedores: backend, MySQL, MongoDB
- Volúmenes persistentes para datos
- Network bridge para comunicación entre contenedores
- Scripts de inicialización automática

## Proyecto Universitario - Bases de Datos

**Objetivos Demostrados:**
- Arquitectura híbrida de bases de datos (MySQL + MongoDB)
- Stored procedures y transacciones ACID
- Integración de bases de datos relacionales y NoSQL
- Dockerización completa de aplicaciones
- Seguridad en aplicaciones web (bcrypt, sessions, RBAC)
- Server-side rendering con Jinja2
- Control de concurrencia con bloqueos (FOR UPDATE)
- Manejo de inventario con actualizaciones atómicas

---

**Sistema Completo:** http://localhost:5001

**Repositorio:** https://github.com/Henry280000/Ordinario_Data_Bases.git

**Desarrollado por:** Henry / Enrique  
**Curso:** Bases de Datos - Proyecto Final  
**Fecha:** Noviembre 2025
