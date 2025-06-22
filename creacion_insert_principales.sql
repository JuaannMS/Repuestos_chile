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

-- Tabla de categorías (id_categoria numérico)
CREATE TABLE categoria (
  id_categoria SERIAL PRIMARY KEY,
  categoria    VARCHAR(100) NOT NULL
);

-- Tabla de tipos de repuesto, con FK que apunta a una columna INTEGER
CREATE TABLE tipo_repuesto (
  id_tipo      SERIAL PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  id_categoria INT REFERENCES categoria(id_categoria)
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
    id_repuesto VARCHAR(20) NOT NULL,
    id_modelo INT NOT NULL,
    PRIMARY KEY (id_repuesto, id_modelo),
    FOREIGN KEY (id_repuesto) REFERENCES Repuestos(id_repuesto),
    FOREIGN KEY (id_modelo) REFERENCES Modelo(id_modelo)
);

-- Tabla: Catalogo
CREATE TABLE Catalogo (
    id_repuesto VARCHAR(20) NOT NULL,
    id_tienda INT NOT NULL,
    PRIMARY KEY (id_repuesto, id_tienda),
    FOREIGN KEY (id_repuesto) REFERENCES Repuestos(id_repuesto),
    FOREIGN KEY (id_tienda) REFERENCES Tienda(id_tienda)
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



INSERT INTO categoria (id_categoria, categoria) VALUES
  (1, 'Motor'),
  (2, 'Frenos'),
  (3, 'Suspensión y dirección'),
  (4, 'Transmisión'),
  (5, 'Sistema eléctrico'),
  (6, 'Sistema de escape'),
  (7, 'Enfriamiento'),
  (8, 'Filtros'),
  (9, 'Carrocería'),
  (10, 'Accesorios');

-- 2) Insertar todos los tipos de repuesto con su id_categoria
INSERT INTO tipo_repuesto (id_tipo, nombre, id_categoria) VALUES
  (1,  'Distribucion',             1),
  (2,  'Kit Rodamiento',           3),
  (3,  'Eje',                      3),
  (4,  'Rodamiento',               3),
  (5,  'Filtro aire',              8),
  (6,  'Bujia',                    1),
  (7,  'Bomba',                    7),
  (8,  'Radiador',                 7),
  (9,  'Correa',                   1),
  (10, 'Enfriador',                7),
  (11, 'Termostato',               1),
  (12, 'Pastilla freno',           2),
  (13, 'Disco freno',              2),
  (14, 'Tambor',                   2),
  (15, 'Sensor',                   5),
  (16, 'Amortiguador',             3),
  (17, 'Espiral',                  3),
  (18, 'Rotula',                   3),
  (19, 'Bieleta',                  3),
  (20, 'Brazo suspension',         3),
  (21, 'Terminal de direccion',    3),
  (22, 'Embrague',                 4),
  (23, 'Caja cambio',              4),
  (24, 'Kit embrague',             4),
  (25, 'Homocinetica',             4),
  (26, 'Alternador',               5),
  (27, 'Bateria',                  5),
  (28, 'Luces',                    5),
  (29, 'Tubo escape',              6),
  (30, 'Ventilador',               7),
  (31, 'Manguera',                 7),
  (32, 'Filtro aceite',            8),
  (33, 'Compresor',                1),
  (34, 'Combustible',              8),
  (35, 'Filtro cabina',            8),
  (36, 'Foco',                     9),
  (37, 'Espejo retrovisor',        9),
  (38, 'Manilla',                  9),
  (39, 'Farol',                    9),
  (40, 'Plumilla',                 10),
  (41, 'Neblinero',                9),
  (42, 'Optico',                   9),
  (43, 'Soporte',                  9),
  (44, 'Tapabarro',                9),
  (45, 'Parachoque',               9),
  (46, 'Motor',                    1),
  (47, 'Luz',                      5),
  (48, 'Filtro',                   8),
  (49, 'Freno',                    2),
  (50, 'Inyector',                 1),
  (51, 'Caneria',                  7),
  (52, 'Bandeja',                  3),
  (53, 'Maza',                     3),
  (54, 'Cremallera',               3),
  (55, 'Flujometro',               5),
  (56, 'Switch',                   5),
  (57, 'Tapa',                     9),
  (58, 'Volante',                  3),
  (59, 'Empaquetadura',            1),
  (60, 'Valvula',                  1),
  (61, 'Cubre tablero',            9),
  (62, 'Brazo auxiliar',           3),
  (63, 'Bobina',                   1),
  (64, 'Espejo',                   9),
  (65, 'Reten',                    1),
  (66, 'Turbo',                    1),
  (67, 'Balancin',                 1),
  (68, 'Anillo',                   1);