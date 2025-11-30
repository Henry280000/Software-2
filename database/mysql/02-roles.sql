USE ecommerce_db;

-- Rol para Administradores
CREATE ROLE IF NOT EXISTS 'ADMIN';

-- Rol para Clientes
CREATE ROLE IF NOT EXISTS 'CLIENTE';

-- Acceso completo a la tabla Inventario
GRANT SELECT, INSERT, UPDATE, DELETE ON ecommerce_db.Inventario TO 'ADMIN';

-- Acceso completo a todas las tablas
GRANT SELECT, INSERT, UPDATE ON ecommerce_db.Usuarios TO 'ADMIN';
GRANT SELECT, INSERT, UPDATE ON ecommerce_db.Pedidos TO 'ADMIN';
GRANT SELECT, INSERT, UPDATE ON ecommerce_db.DetallePedido TO 'ADMIN';

-- Permiso para ejecutar el stored procedure de actualización de stock
GRANT EXECUTE ON PROCEDURE ecommerce_db.sp_actualizar_stock TO 'ADMIN';
GRANT EXECUTE ON PROCEDURE ecommerce_db.sp_crear_pedido TO 'ADMIN';

-- Solo lectura en Inventario (ver productos disponibles)
GRANT SELECT ON ecommerce_db.Inventario TO 'CLIENTE';

-- Solo lectura de su propia información
GRANT SELECT ON ecommerce_db.Usuarios TO 'CLIENTE';

-- Acceso a pedidos (crear y consultar sus propios pedidos)
GRANT SELECT, INSERT ON ecommerce_db.Pedidos TO 'CLIENTE';
GRANT SELECT, INSERT ON ecommerce_db.DetallePedido TO 'CLIENTE';

-- Permiso para ejecutar solo el stored procedure de crear pedido
GRANT EXECUTE ON PROCEDURE ecommerce_db.sp_crear_pedido TO 'CLIENTE';

-- Usuario Admin (para la aplicación)
CREATE USER IF NOT EXISTS 'admin_user'@'%' IDENTIFIED BY 'admin_secure_pass_2024';
GRANT 'ADMIN' TO 'admin_user'@'%';
SET DEFAULT ROLE 'ADMIN' TO 'admin_user'@'%';

-- Usuario Cliente (para la aplicación)
CREATE USER IF NOT EXISTS 'cliente_user'@'%' IDENTIFIED BY 'cliente_secure_pass_2024';
GRANT 'CLIENTE' TO 'cliente_user'@'%';
SET DEFAULT ROLE 'CLIENTE' TO 'cliente_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Mostrar roles creados
SELECT 'Roles creados correctamente' AS status;
SHOW GRANTS FOR 'ADMIN';
SHOW GRANTS FOR 'CLIENTE';

-- Mostrar usuarios y sus roles
SELECT 'Usuarios creados correctamente' AS status;
