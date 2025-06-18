-- Tabla: Marca
CREATE TABLE Marca (
    id_marca SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla: Modelo
CREATE TABLE Modelo (
    id_modelo SERIAL PRIMARY KEY,
    id_marca INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_marca) REFERENCES Marca(id_marca)
);

-- Tabla: Tipo de repuesto
CREATE TABLE Tipo_repuesto (
    id_tipo SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla: Tienda
CREATE TABLE Tienda (
    id_tienda SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla: Repuestos
CREATE TABLE Repuestos (
    id_repuesto VARCHAR(20) PRIMARY KEY,
    nombre TEXT NOT NULL,
    id_modelo INT NOT NULL,
    id_tipo INT NOT NULL,
    id_tienda INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    link TEXT,
    descripcion TEXT,
    imagen TEXT,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_modelo) REFERENCES Modelo(id_modelo),
    FOREIGN KEY (id_tipo) REFERENCES Tipo_repuesto(id_tipo),
    FOREIGN KEY (id_tienda) REFERENCES Tienda(id_tienda)
);
-- Tabla: Usuario
CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    contrasena VARCHAR(255) NOT NULL,
	rol TEXT NOT NULL CHECK (rol IN ('admin', 'cliente')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Favoritos
CREATE TABLE Favoritos (
    id_favorito SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_repuesto VARCHAR(10) NOT NULL,
	FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_repuesto) REFERENCES Repuestos(id_repuesto)
);

-- Tabla: Compatibilidad
CREATE TABLE Compatibilidad (
    id_repuesto VARCHAR(10) NOT NULL,
    id_modelo INT NOT NULL,
    PRIMARY KEY (id_repuesto, id_modelo),
    FOREIGN KEY (id_repuesto) REFERENCES Repuestos(id_repuesto),
    FOREIGN KEY (id_modelo) REFERENCES Modelo(id_modelo)
);

-- Tabla: Catalogo
CREATE TABLE Catalogo (
    id_repuesto VARCHAR(10) NOT NULL,
    id_modelo INT NOT NULL,
    PRIMARY KEY (id_repuesto, id_modelo),
    FOREIGN KEY (id_repuesto) REFERENCES Repuestos(id_repuesto),
    FOREIGN KEY (id_modelo) REFERENCES Modelo(id_modelo)
);





INSERT INTO Marca (id_marca, nombre) VALUES (1, 'Chevrolet');
INSERT INTO Marca (id_marca, nombre) VALUES (2, 'Hyundai');
INSERT INTO Marca (id_marca, nombre) VALUES (3, 'Nissan');
INSERT INTO Marca (id_marca, nombre) VALUES (4, 'Toyota');
INSERT INTO Marca (id_marca, nombre) VALUES (5, 'Kia');
INSERT INTO Marca (id_marca, nombre) VALUES (6, 'Susuki');
INSERT INTO Marca (id_marca, nombre) VALUES (7, 'Peugeot');
INSERT INTO Marca (id_marca, nombre) VALUES (8, 'Ford');
INSERT INTO Marca (id_marca, nombre) VALUES (9, 'Mazda');
INSERT INTO Marca (id_marca, nombre) VALUES (10, 'Mitsubishi');

INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (1, 1, 'Spark');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (2, 1, 'Aveo');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (3, 1, 'Sail');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (4, 1, 'Cruze');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (5, 1, 'Malibu');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (6, 1, 'Tracker');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (7, 1, 'Captiva');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (8, 1, 'S10');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (9, 2, 'Accent');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (10, 2, 'Elantra');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (11, 2, 'Sonata');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (12, 2, 'Tucson');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (13, 2, 'Santa Fe');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (14, 2, 'Creta');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (15, 2, 'i10');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (16, 2, 'Kona');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (17, 3, 'Sentra');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (18, 3, 'Altima');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (19, 3, 'Versa');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (20, 3, 'March');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (21, 3, 'X-Trail');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (22, 3, 'Pathfinder');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (23, 3, 'Frontier');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (24, 3, 'Z Series');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (25, 4, 'Corolla');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (26, 4, 'Camry');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (27, 4, 'Yaris');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (28, 4, 'Hilux');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (29, 4, 'RAV4');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (30, 4, 'Land Cruiser');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (31, 4, 'Prius');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (32, 4, 'Supra');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (33, 5, 'Picanto');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (34, 5, 'Rio');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (35, 5, 'Cerato');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (36, 5, 'Sportage');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (37, 5, 'Sorento');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (38, 5, 'Soul');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (39, 5, 'Seltos');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (40, 5, 'Carnival');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (41, 6, 'Swift');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (42, 6, 'Alto');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (43, 6, 'Baleno');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (44, 6, 'Celerio');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (45, 6, 'Vitara');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (46, 6, 'Jimny');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (47, 6, 'SX4');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (48, 6, 'Ertiga');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (49, 7, '208');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (50, 7, '308');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (51, 7, '508');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (52, 7, '2008');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (53, 7, '3008');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (54, 7, '5008');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (55, 7, 'Partner');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (56, 7, 'Rifter');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (57, 8, 'Fiesta');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (58, 8, 'Focus');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (59, 8, 'Mustang');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (60, 8, 'Ranger');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (61, 8, 'F-150');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (62, 8, 'Escape');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (63, 8, 'Explorer');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (64, 8, 'Maverick');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (65, 9, 'Mazda2');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (66, 9, 'Mazda3');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (67, 9, 'Mazda6');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (68, 9, 'CX-3');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (69, 9, 'CX-5');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (70, 9, 'CX-9');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (71, 9, 'BT-50');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (72, 9, 'MX-5');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (73, 10, 'Lancer');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (74, 10, 'Mirage');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (75, 10, 'Outlander');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (76, 10, 'Outlander Sport');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (77, 10, 'ASX');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (78, 10, 'Eclipse Cross');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (79, 10, 'Montero Sport');
INSERT INTO Modelo (id_modelo, id_marca, nombre) VALUES (80, 10, 'L200');

INSERT INTO Tienda (id_tienda, nombre) VALUES (1, 'Autoplanet');
INSERT INTO Tienda (id_tienda, nombre) VALUES (2, 'Casa de Repuestos');
INSERT INTO Tienda (id_tienda, nombre) VALUES (3, 'ChileRepuestos');
INSERT INTO Tienda (id_tienda, nombre) VALUES (4, 'Ciper');
INSERT INTO Tienda (id_tienda, nombre) VALUES (5, 'Emgi');
INSERT INTO Tienda (id_tienda, nombre) VALUES (6, 'Inalco');
INSERT INTO Tienda (id_tienda, nombre) VALUES (7, 'Mundo Repuestos');
INSERT INTO Tienda (id_tienda, nombre) VALUES (8, 'Salfa Repuestos');
INSERT INTO Tienda (id_tienda, nombre) VALUES (9, 'Takora');
INSERT INTO Tienda (id_tienda, nombre) VALUES (10, 'Ulti');

INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (1, 'Filtro de aceite');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (2, 'Kit rodamiento');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (3, 'Neumático');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (4, 'Filtros de aire');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (5, 'Bujías');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (6, 'Bomba');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (7, 'Radiador');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (8, 'Correas');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (9, 'Termostato');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (10, 'Pastillas de freno');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (11, 'Discos de freno');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (12, 'Tambor');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (13, 'Sensor');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (14, 'Amortiguador');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (15, 'Espiral');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (16, 'Rótula');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (17, 'Bieleta');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (18, 'Brazo de suspensión');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (19, 'Terminal de dirección');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (20, 'Embragues');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (21, 'Caja de cambio');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (22, 'Kit de embrague');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (23, 'Homocinética');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (24, 'Alternador');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (25, 'Batería');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (26, 'Luces');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (27, 'Tubo de escape');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (28, 'Ventilador');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (29, 'Manguera');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (30, 'Compresor');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (31, 'Combustible');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (32, 'Filtro cabina');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (33, 'Foco');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (34, 'Espejo retrovisor');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (35, 'Manilla de puerta');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (36, 'Plumilla');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (37, 'Tapabarros');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (38, 'Parachoque');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (39, 'Motor');
INSERT INTO tipo_repuesto (id_tipo, nombre) VALUES (40, 'Luz');