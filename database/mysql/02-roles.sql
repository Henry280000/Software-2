USE ecommerce_db;

-- Usuario root de la aplicación con todos los privilegios
-- La aplicación usa este usuario para todas las operaciones
-- El control de acceso ADMIN/CLIENTE se maneja en la capa de aplicación

-- Nota: El usuario 'root' ya existe en MySQL, solo aplicamos privilegios
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'root'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

SELECT 'Privilegios configurados correctamente' AS status;
