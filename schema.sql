-- Base de Datos de Refugio de Mascotas - Versión Completa con Campo Animal
-- Adminer 5.3.0 MySQL 8.0.41 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

-- =============================================
-- TABLA: refugios
-- =============================================
DROP TABLE IF EXISTS `refugios`;
CREATE TABLE `refugios` (
  `idRefugio` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `telefono` decimal(10,0) DEFAULT NULL,
  `correoElectronico` varchar(50) DEFAULT NULL,
  `capacidad` int DEFAULT NULL,
  `fechaFundacion` date DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  PRIMARY KEY (`idRefugio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `refugios` (`idRefugio`, `nombre`, `direccion`, `telefono`, `correoElectronico`, `capacidad`, `fechaFundacion`, `descripcion`) VALUES
(1, 'Refugio Esperanza Animal', 'Av. Principal 123, Col. Centro', 8621234567, 'contacto@esperanzaanimal.org', 50, '2018-03-15', 'Refugio dedicado al rescate y cuidado de perros y gatos abandonados.'),
(2, 'Casa de Amor Perruno', 'Calle Libertad 456, Col. Norte', 8629876543, 'info@casaamorperruno.com', 30, '2020-07-10', 'Refugio especializado en perros de la calle y casos de maltrato.');

-- =============================================
-- TABLA: adoptantes
-- =============================================
DROP TABLE IF EXISTS `adoptantes`;
CREATE TABLE `adoptantes` (
  `idAdoptante` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `sexo` varchar(10) NOT NULL,
  `telefono` decimal(10,0) NOT NULL,
  `correoElectronico` varchar(50) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `experienciaConMascotas` varchar(200) DEFAULT NULL,
  `tipoVivienda` varchar(50) DEFAULT NULL,
  `tipo_usuario` varchar(20) DEFAULT 'adoptante',
  PRIMARY KEY (`idAdoptante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `adoptantes` (`idAdoptante`, `nombre`, `sexo`, `telefono`, `correoElectronico`, `password`, `direccion`, `experienciaConMascotas`, `tipoVivienda`) VALUES
(1, 'Maria Rodriguez', 'F', 8625551234, 'maria.rodriguez@email.com', 'password123', 'Calle Flores 789, Col. Sur', 'Ha tenido perros por 10 años', 'Casa con patio'),
(2, 'Carlos Martinez', 'M', 8625559876, 'carlos.martinez@email.com', 'password456', 'Av. Juarez 321, Col. Este', 'Primera vez con mascota', 'Departamento');

-- =============================================
-- TABLA: mascotas (CON CAMPO ANIMAL)
-- =============================================
DROP TABLE IF EXISTS `mascotas`;
CREATE TABLE `mascotas` (
  `idMascota` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `animal` varchar(50) NOT NULL,
  `sexo` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `raza` varchar(100) DEFAULT NULL,
  `peso` double NOT NULL,
  `condiciones` varchar(100) DEFAULT NULL,
  `idRefugio` bigint NOT NULL,
  `fechaIngreso` date DEFAULT NULL,
  `edad` int DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Disponible',
  PRIMARY KEY (`idMascota`),
  KEY `idRefugio` (`idRefugio`),
  CONSTRAINT `mascotas_ibfk_1` FOREIGN KEY (`idRefugio`) REFERENCES `refugios` (`idRefugio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `mascotas` (`idMascota`, `nombre`, `animal`, `sexo`, `raza`, `peso`, `condiciones`, `idRefugio`, `fechaIngreso`, `edad`, `estado`) VALUES
(1, 'Chaparro', 'Perro', 'M', 'Mestizo', 10, 'Tiene un problema en el estomago, necesita 2 operaciones.', 1, '2024-01-15', 3, 'En tratamiento'),
(2, 'Luna', 'Perro', 'F', 'Labrador', 25, 'Saludable', 1, '2024-02-20', 2, 'Disponible'),
(3, 'Max', 'Perro', 'M', 'Pastor Alemán', 30, 'Cojea de la pata trasera izquierda', 2, '2024-03-10', 5, 'Disponible'),
(4, 'Mimi', 'Gato', 'F', 'Siamés', 4, 'Saludable', 1, '2024-04-05', 1, 'Disponible'),
(5, 'Pelusa', 'Conejo', 'F', 'Angora', 2, 'Necesita dieta especial', 2, '2024-05-12', 2, 'Disponible'),
(6, 'Pico', 'Ave', 'M', 'Canario', 0.05, 'Ala izquierda fracturada en recuperación', 1, '2024-06-01', 1, 'En tratamiento');

-- =============================================
-- TABLA: adopciones
-- =============================================
DROP TABLE IF EXISTS `adopciones`;
CREATE TABLE `adopciones` (
  `idAdopcion` bigint NOT NULL AUTO_INCREMENT,
  `idMascota` bigint NOT NULL,
  `idAdoptante` bigint NOT NULL,
  `fechaSolicitud` date NOT NULL,
  `fechaAdopcion` date DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'En proceso',
  `observaciones` text DEFAULT NULL,
  `costoAdopcion` double DEFAULT 0,
  PRIMARY KEY (`idAdopcion`),
  KEY `idMascota` (`idMascota`),
  KEY `idAdoptante` (`idAdoptante`),
  CONSTRAINT `adopciones_ibfk_1` FOREIGN KEY (`idMascota`) REFERENCES `mascotas` (`idMascota`),
  CONSTRAINT `adopciones_ibfk_2` FOREIGN KEY (`idAdoptante`) REFERENCES `adoptantes` (`idAdoptante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `adopciones` (`idAdopcion`, `idMascota`, `idAdoptante`, `fechaSolicitud`, `fechaAdopcion`, `estado`, `observaciones`, `costoAdopcion`) VALUES
(1, 2, 1, '2024-08-15', '2024-08-20', 'Finalizada', 'Adopción exitosa. La familia tiene experiencia con perros.', 500),
(2, 3, 2, '2024-08-25', NULL, 'En proceso', 'Pendiente visita domiciliaria.', 0),
(3, 4, 1, '2024-08-30', NULL, 'En proceso', 'Interesada en adoptar también un gato.', 0);

-- =============================================
-- TABLA: padrinos
-- =============================================
DROP TABLE IF EXISTS `padrinos`;
CREATE TABLE `padrinos` (
  `idPadrino` bigint NOT NULL AUTO_INCREMENT,
  `nombrePadrino` varchar(100) NOT NULL,
  `sexo` varchar(10) NOT NULL,
  `telefono` decimal(10,0) NOT NULL,
  `correoElectronico` varchar(50) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`idPadrino`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `padrinos` (`idPadrino`, `nombrePadrino`, `sexo`, `telefono`, `correoElectronico`, `password`) VALUES
(1, 'Jose Perez', 'M', 8621234567, 'jose.perez@gmail.com', 'padrino123'),
(2, 'Ana Garcia', 'F', 8625554321, 'ana.garcia@email.com', 'padrino456'),
(3, 'Roberto Silva', 'M', 8625557890, 'roberto.silva@email.com', 'padrino789');

-- =============================================
-- TABLA: apoyos
-- =============================================
DROP TABLE IF EXISTS `apoyos`;
CREATE TABLE `apoyos` (
  `idApoyo` bigint NOT NULL AUTO_INCREMENT,
  `idMascota` bigint DEFAULT NULL,
  `idPadrino` bigint NOT NULL,
  `idRefugio` bigint DEFAULT NULL,
  `monto` double NOT NULL,
  `causa` varchar(100) DEFAULT NULL,
  `fechaApoyo` date DEFAULT NULL,
  PRIMARY KEY (`idApoyo`),
  KEY `idMascota` (`idMascota`),
  KEY `idPadrino` (`idPadrino`),
  KEY `idRefugio` (`idRefugio`),
  CONSTRAINT `apoyos_ibfk_1` FOREIGN KEY (`idMascota`) REFERENCES `mascotas` (`idMascota`),
  CONSTRAINT `apoyos_ibfk_2` FOREIGN KEY (`idPadrino`) REFERENCES `padrinos` (`idPadrino`),
  CONSTRAINT `apoyos_ibfk_3` FOREIGN KEY (`idRefugio`) REFERENCES `refugios` (`idRefugio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `apoyos` (`idApoyo`, `idMascota`, `idPadrino`, `idRefugio`, `monto`, `causa`, `fechaApoyo`) VALUES
(1, 1, 1, NULL, 1000, 'Pago de una operacion.', '2024-08-01'),
(2, NULL, 1, 1, 500, 'Apoyo al refugio.', '2024-08-15'),
(3, 2, 2, NULL, 300, 'Vacunas y desparasitación.', '2024-08-10'),
(4, 6, 3, NULL, 200, 'Tratamiento veterinario para fractura de ala.', '2024-08-20'),
(5, NULL, 2, 2, 750, 'Compra de alimento especializado.', '2024-08-25');

-- =============================================
-- VISTAS ÚTILES
-- =============================================

-- Vista: Mascotas con información del refugio (ACTUALIZADA CON ANIMAL)
DROP VIEW IF EXISTS `vista_mascotas_refugio`;
CREATE VIEW `vista_mascotas_refugio` AS
SELECT 
    m.idMascota,
    m.nombre AS nombreMascota,
    m.animal,
    m.sexo,
    m.raza,
    m.peso,
    m.condiciones,
    m.edad,
    m.estado,
    r.nombre AS nombreRefugio,
    r.telefono AS telefonoRefugio
FROM mascotas m
JOIN refugios r ON m.idRefugio = r.idRefugio;

-- Vista: Resumen de apoyos por refugio
DROP VIEW IF EXISTS `vista_apoyos_refugio`;
CREATE VIEW `vista_apoyos_refugio` AS
SELECT 
    r.nombre AS refugio,
    COUNT(a.idApoyo) AS totalApoyos,
    SUM(a.monto) AS montoTotal
FROM refugios r
LEFT JOIN apoyos a ON r.idRefugio = a.idRefugio OR r.idRefugio IN (
    SELECT m.idRefugio FROM mascotas m WHERE m.idMascota = a.idMascota
)
GROUP BY r.idRefugio, r.nombre;

-- Vista: Estado de adopciones (ACTUALIZADA CON ANIMAL)
DROP VIEW IF EXISTS `vista_adopciones_detalle`;
CREATE VIEW `vista_adopciones_detalle` AS
SELECT 
    ad.idAdopcion,
    m.nombre AS nombreMascota,
    m.animal,
    m.raza,
    a.nombre AS nombreAdoptante,
    a.telefono,
    ad.fechaSolicitud,
    ad.fechaAdopcion,
    ad.estado,
    ad.costoAdopcion
FROM adopciones ad
JOIN mascotas m ON ad.idMascota = m.idMascota
JOIN adoptantes a ON ad.idAdoptante = a.idAdoptante;

-- Vista: Estadísticas por tipo de animal
DROP VIEW IF EXISTS `vista_estadisticas_animales`;
CREATE VIEW `vista_estadisticas_animales` AS
SELECT 
    m.animal,
    COUNT(*) AS totalMascotas,
    SUM(CASE WHEN m.estado = 'Disponible' THEN 1 ELSE 0 END) AS disponibles,
    SUM(CASE WHEN m.estado = 'En tratamiento' THEN 1 ELSE 0 END) AS enTratamiento,
    SUM(CASE WHEN m.estado = 'Adoptada' THEN 1 ELSE 0 END) AS adoptadas,
    AVG(m.peso) AS pesoPromedio,
    AVG(m.edad) AS edadPromedio
FROM mascotas m
GROUP BY m.animal
ORDER BY totalMascotas DESC;
