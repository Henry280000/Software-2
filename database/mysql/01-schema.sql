-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('ADMIN', 'CLIENTE') DEFAULT 'CLIENTE',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_rol (rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Inventario (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    producto_id VARCHAR(50) NOT NULL COMMENT 'Referencia al ID del jersey en MongoDB',
    nombre_producto VARCHAR(200) NOT NULL,
    talla VARCHAR(10) NOT NULL,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (cantidad_disponible >= 0),
    CHECK (precio_unitario > 0),
    INDEX idx_sku (sku),
    INDEX idx_producto_id (producto_id),
    INDEX idx_disponibilidad (cantidad_disponible)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL,
    estado ENUM('PENDIENTE', 'PROCESANDO', 'COMPLETADO', 'CANCELADO') DEFAULT 'PENDIENTE',
    direccion_envio TEXT,
    notas TEXT,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_fecha (fecha_pedido),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS DetallePedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    sku VARCHAR(50) NOT NULL,
    nombre_producto VARCHAR(200) NOT NULL,
    talla VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES Inventario(sku) ON DELETE RESTRICT,
    CHECK (cantidad > 0),
    INDEX idx_pedido (id_pedido),
    INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELIMITER //

CREATE PROCEDURE sp_crear_pedido(
    IN p_id_usuario INT,
    IN p_direccion_envio TEXT,
    IN p_items JSON,
    OUT p_id_pedido INT,
    OUT p_mensaje VARCHAR(500)
)
BEGIN
    DECLARE v_total DECIMAL(10, 2) DEFAULT 0;
    DECLARE v_sku VARCHAR(50);
    DECLARE v_cantidad INT;
    DECLARE v_cantidad_disponible INT;
    DECLARE v_precio_unitario DECIMAL(10, 2);
    DECLARE v_nombre_producto VARCHAR(200);
    DECLARE v_talla VARCHAR(10);
    DECLARE v_subtotal DECIMAL(10, 2);
    DECLARE v_index INT DEFAULT 0;
    DECLARE v_items_count INT;
    DECLARE v_item JSON;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_mensaje = 'Error: La transacción ha sido revertida';
        SET p_id_pedido = NULL;
    END;
    
    -- Iniciar transacción
    START TRANSACTION;
    
    -- Validar usuario
    IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE id_usuario = p_id_usuario AND activo = TRUE) THEN
        SET p_mensaje = 'Error: Usuario no válido o inactivo';
        SET p_id_pedido = NULL;
        ROLLBACK;
    ELSE
        -- Obtener cantidad de items
        SET v_items_count = JSON_LENGTH(p_items);
        
        -- Crear el pedido
        INSERT INTO Pedidos (id_usuario, direccion_envio, total, estado)
        VALUES (p_id_usuario, p_direccion_envio, 0, 'PENDIENTE');
        
        SET p_id_pedido = LAST_INSERT_ID();
        
        -- Procesar cada item del pedido
        item_loop: WHILE v_index < v_items_count DO
            SET v_item = JSON_EXTRACT(p_items, CONCAT('$[', v_index, ']'));
            SET v_sku = JSON_UNQUOTE(JSON_EXTRACT(v_item, '$.sku'));
            SET v_cantidad = JSON_EXTRACT(v_item, '$.cantidad');
            
            -- Bloquear la fila del inventario para evitar concurrencia
            SELECT cantidad_disponible, precio_unitario, nombre_producto, talla
            INTO v_cantidad_disponible, v_precio_unitario, v_nombre_producto, v_talla
            FROM Inventario
            WHERE sku = v_sku
            FOR UPDATE;
            
            -- Verificar disponibilidad
            IF v_cantidad_disponible IS NULL THEN
                SET p_mensaje = CONCAT('Error: Producto con SKU ', v_sku, ' no encontrado');
                ROLLBACK;
                LEAVE item_loop;
            ELSEIF v_cantidad_disponible < v_cantidad THEN
                SET p_mensaje = CONCAT('Error: Stock insuficiente para SKU ', v_sku, 
                                      '. Disponible: ', v_cantidad_disponible, 
                                      ', Solicitado: ', v_cantidad);
                ROLLBACK;
                LEAVE item_loop;
            ELSE
                -- Calcular subtotal
                SET v_subtotal = v_precio_unitario * v_cantidad;
                SET v_total = v_total + v_subtotal;
                
                -- Insertar detalle del pedido
                INSERT INTO DetallePedido (id_pedido, sku, nombre_producto, talla, cantidad, precio_unitario, subtotal)
                VALUES (p_id_pedido, v_sku, v_nombre_producto, v_talla, v_cantidad, v_precio_unitario, v_subtotal);
                
                -- Actualizar inventario
                UPDATE Inventario
                SET cantidad_disponible = cantidad_disponible - v_cantidad
                WHERE sku = v_sku;
            END IF;
            
            SET v_index = v_index + 1;
        END WHILE item_loop;
        
        -- Actualizar total del pedido
        UPDATE Pedidos
        SET total = v_total, estado = 'PROCESANDO'
        WHERE id_pedido = p_id_pedido;
        
        -- Confirmar transacción
        COMMIT;
        SET p_mensaje = CONCAT('Pedido creado exitosamente. Total: $', v_total);
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE sp_actualizar_stock(
    IN p_sku VARCHAR(50),
    IN p_cantidad_adicional INT,
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_cantidad_actual INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_mensaje = 'Error al actualizar el stock';
    END;
    
    START TRANSACTION;
    
    -- Verificar que el producto existe
    SELECT cantidad_disponible INTO v_cantidad_actual
    FROM Inventario
    WHERE sku = p_sku
    FOR UPDATE;
    
    IF v_cantidad_actual IS NULL THEN
        SET p_mensaje = CONCAT('Error: Producto con SKU ', p_sku, ' no encontrado');
        ROLLBACK;
    ELSE
        UPDATE Inventario
        SET cantidad_disponible = cantidad_disponible + p_cantidad_adicional
        WHERE sku = p_sku;
        
        COMMIT;
        SET p_mensaje = CONCAT('Stock actualizado. Nueva cantidad: ', v_cantidad_actual + p_cantidad_adicional);
    END IF;
END //

DELIMITER ;

-- Insertar usuarios de prueba
INSERT INTO Usuarios (nombre, email, password_hash, rol) VALUES
('Administrador', 'admin@jerseys.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqGRzFvBd6', 'ADMIN'),
('Juan Pérez', 'juan@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqGRzFvBd6', 'CLIENTE'),
('María García', 'maria@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqGRzFvBd6', 'CLIENTE');

-- Insertar inventario de prueba (36 SKUs: 9 equipos x 4 tallas)
INSERT INTO Inventario (sku, producto_id, nombre_producto, talla, cantidad_disponible, precio_unitario) VALUES
-- Barcelona
('BAR-HOME-2024-S', 'jersey_bar_home_2024', 'Barcelona Jersey Home 2024', 'S', 35, 89.99),
('BAR-HOME-2024-M', 'jersey_bar_home_2024', 'Barcelona Jersey Home 2024', 'M', 40, 89.99),
('BAR-HOME-2024-L', 'jersey_bar_home_2024', 'Barcelona Jersey Home 2024', 'L', 35, 89.99),
('BAR-HOME-2024-XL', 'jersey_bar_home_2024', 'Barcelona Jersey Home 2024', 'XL', 28, 89.99),
-- Real Madrid
('RM-HOME-2024-S', 'jersey_rm_home_2024', 'Real Madrid Jersey Home 2024', 'S', 45, 89.99),
('RM-HOME-2024-M', 'jersey_rm_home_2024', 'Real Madrid Jersey Home 2024', 'M', 50, 89.99),
('RM-HOME-2024-L', 'jersey_rm_home_2024', 'Real Madrid Jersey Home 2024', 'L', 30, 89.99),
('RM-HOME-2024-XL', 'jersey_rm_home_2024', 'Real Madrid Jersey Home 2024', 'XL', 25, 89.99),
-- Manchester United
('MAN-HOME-2024-S', 'jersey_man_home_2024', 'Manchester United Jersey Home 2024', 'S', 40, 79.99),
('MAN-HOME-2024-M', 'jersey_man_home_2024', 'Manchester United Jersey Home 2024', 'M', 45, 79.99),
('MAN-HOME-2024-L', 'jersey_man_home_2024', 'Manchester United Jersey Home 2024', 'L', 38, 79.99),
('MAN-HOME-2024-XL', 'jersey_man_home_2024', 'Manchester United Jersey Home 2024', 'XL', 32, 79.99),
-- Liverpool
('LIV-HOME-2024-S', 'jersey_liv_home_2024', 'Liverpool Jersey Home 2024', 'S', 38, 79.99),
('LIV-HOME-2024-M', 'jersey_liv_home_2024', 'Liverpool Jersey Home 2024', 'M', 42, 79.99),
('LIV-HOME-2024-L', 'jersey_liv_home_2024', 'Liverpool Jersey Home 2024', 'L', 33, 79.99),
('LIV-HOME-2024-XL', 'jersey_liv_home_2024', 'Liverpool Jersey Home 2024', 'XL', 30, 79.99),
-- PSG
('PSG-HOME-2024-S', 'jersey_psg_home_2024', 'PSG Jersey Home 2024', 'S', 28, 84.99),
('PSG-HOME-2024-M', 'jersey_psg_home_2024', 'PSG Jersey Home 2024', 'M', 30, 84.99),
('PSG-HOME-2024-L', 'jersey_psg_home_2024', 'PSG Jersey Home 2024', 'L', 25, 84.99),
('PSG-HOME-2024-XL', 'jersey_psg_home_2024', 'PSG Jersey Home 2024', 'XL', 22, 84.99),
-- Bayern Munich
('BAY-HOME-2024-S', 'jersey_bay_home_2024', 'Bayern Munich Jersey Home 2024', 'S', 32, 84.99),
('BAY-HOME-2024-M', 'jersey_bay_home_2024', 'Bayern Munich Jersey Home 2024', 'M', 35, 84.99),
('BAY-HOME-2024-L', 'jersey_bay_home_2024', 'Bayern Munich Jersey Home 2024', 'L', 30, 84.99),
('BAY-HOME-2024-XL', 'jersey_bay_home_2024', 'Bayern Munich Jersey Home 2024', 'XL', 28, 84.99),
-- Club América
('AME-HOME-2024-S', 'jersey_ame_home_2024', 'Club América Jersey Home 2024', 'S', 40, 84.99),
('AME-HOME-2024-M', 'jersey_ame_home_2024', 'Club América Jersey Home 2024', 'M', 45, 84.99),
('AME-HOME-2024-L', 'jersey_ame_home_2024', 'Club América Jersey Home 2024', 'L', 38, 84.99),
('AME-HOME-2024-XL', 'jersey_ame_home_2024', 'Club América Jersey Home 2024', 'XL', 35, 84.99),
-- Borussia Dortmund
('DOR-HOME-2024-S', 'jersey_dor_home_2024', 'Borussia Dortmund Jersey Home 2024', 'S', 35, 79.99),
('DOR-HOME-2024-M', 'jersey_dor_home_2024', 'Borussia Dortmund Jersey Home 2024', 'M', 40, 79.99),
('DOR-HOME-2024-L', 'jersey_dor_home_2024', 'Borussia Dortmund Jersey Home 2024', 'L', 35, 79.99),
('DOR-HOME-2024-XL', 'jersey_dor_home_2024', 'Borussia Dortmund Jersey Home 2024', 'XL', 30, 79.99),
-- Inter Miami
('MIA-HOME-2024-S', 'jersey_mia_home_2024', 'Inter Miami Jersey Home 2024', 'S', 38, 84.99),
('MIA-HOME-2024-M', 'jersey_mia_home_2024', 'Inter Miami Jersey Home 2024', 'M', 42, 84.99),
('MIA-HOME-2024-L', 'jersey_mia_home_2024', 'Inter Miami Jersey Home 2024', 'L', 36, 84.99),
('MIA-HOME-2024-XL', 'jersey_mia_home_2024', 'Inter Miami Jersey Home 2024', 'XL', 33, 84.99);

SELECT 'Base de datos MySQL inicializada correctamente' AS status;
SELECT COUNT(*) AS total_usuarios FROM Usuarios;
SELECT COUNT(*) AS total_inventario FROM Inventario;
