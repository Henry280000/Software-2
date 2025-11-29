# E-Commerce - MySQL + MongoDB + Docker

Sistema de comercio electrónico con arquitectura híbrida de bases de datos.

## Inicio Rápido

```bash
# 1. Levantar el sistema
docker-compose up -d

# 2. Cargar datos iniciales
docker exec backend_ecommerce python /app/scripts/sync_inventory.py

# 3. Acceder: http://localhost:5001
```

## Credenciales

| Rol | Email | Password |
|-----|-------|----------|
| Cliente | test@test.com | Test123! |
| Admin | admin@jerseys.com | Admin123! |

## Arquitectura

```
┌──────────────────────────────────────────────────┐
│  Frontend: HTML + CSS + JavaScript (minimal)     │
│  Backend: Python 3.11 + Flask 3.0 + Jinja2      │
│  ├── MySQL 8.0: Transacciones                    │
│  │   ├── Usuarios                                │
│  │   ├── Pedidos                                 │
│  │   ├── DetallePedido                           │
│  │   └── Inventario (26 items)                   │
│  └── MongoDB 6.0: Catálogo                       │
│      ├── jerseys (6 productos)                   │
│      ├── comentarios                             │
│      └── logs                                    │
└──────────────────────────────────────────────────┘
```

## Estructura del Proyecto

```
ordinario/
├── backend/
│   ├── app_new.py              # Aplicación principal (SE USA)
│   ├── app_old.py              # Archivo antiguo (NO SE USA)
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

## Funcionalidades

### Para Todos los Usuarios
- Ver catálogo de productos
- Buscar jerseys por equipo/marca
- Ver detalles de producto
- Agregar al carrito
- Gestionar carrito (cantidades, eliminar)

### Para Usuarios Registrados
- Login/Logout con sesiones
- Registro de nuevos usuarios
- Realizar compras
- Ver historial de pedidos
- Ver detalles de pedidos

### Para Administradores
- Dashboard con estadísticas
- Ver todos los pedidos
- Gestión de inventario

## Comandos Útiles

### Docker
```bash
# Ver logs del backend
docker logs backend_ecommerce -f

# Ver todos los contenedores
docker ps

# Reiniciar backend
docker-compose restart backend

# Detener todo
docker-compose down

# Resetear bases de datos
docker-compose down -v
docker-compose up -d
```

### Base de Datos
```bash
# Conectar a MySQL
docker exec -it mysql_ecommerce mysql -u ecommerce_user -pecommerce_pass ecommerce_db

# Conectar a MongoDB
docker exec -it mongodb_ecommerce mongosh -u admin -p adminpassword --authenticationDatabase admin

# Ver usuarios
docker exec mysql_ecommerce mysql -u ecommerce_user -pecommerce_pass -e "SELECT * FROM Usuarios;" ecommerce_db

# Ver inventario
docker exec mysql_ecommerce mysql -u ecommerce_user -pecommerce_pass -e "SELECT * FROM Inventario;" ecommerce_db
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

## Base de Datos

### MySQL (Transacciones ACID)
```sql
Usuarios        # Autenticación (4 usuarios)
Pedidos         # Órdenes de compra
DetallePedido   # Items de cada pedido
Inventario      # Stock por SKU (26 items)
```

### MongoDB (Catálogo Flexible)
```javascript
jerseys      // 6 productos
comentarios  // Reseñas
logs         // Auditoría
```

## Seguridad

- Contraseñas hasheadas con bcrypt
- Sesiones del lado del servidor (Flask Sessions)
- Validación de roles (Admin vs Cliente)
- Prepared statements (previene SQL injection)
- Validación de entrada en servidor

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

## Notas Importantes

- **JavaScript es OPCIONAL:** La funcionalidad core funciona sin JavaScript
- **Server-Side Rendering:** Todo se renderiza en el servidor (más rápido y seguro)
- **Archivos Obsoletos:** Los archivos antiguos están en `backend/static/archivos_antiguos/`
- **app.py → app_old.py:** El archivo antiguo ya no se usa

## Proyecto Universitario

Este proyecto demuestra:
- Arquitectura híbrida de bases de datos
- Stored procedures y transacciones ACID
- Integración de MySQL y MongoDB
- Dockerización de aplicaciones
- Seguridad en aplicaciones web
- Server-side rendering con Jinja2

---

**Sistema listo:** http://localhost:5001

**Desarrollado por:** Henry / Enrique  
**Universidad:** [Nombre Universidad]  
**Curso:** Bases de Datos  
**Fecha:** Noviembre 2025
