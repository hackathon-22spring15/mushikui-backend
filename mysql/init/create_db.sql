DROP DATABASE IF EXISTS mushikui;
CREATE DATABASE mushikui;
USE mushikui;

CREATE TABLE IF NOT EXISTS `problems` (
    `id` int(11) AUTO_INCREMENT PRIMARY KEY NOT NULL,
    `expression` varchar(32) NOT NULL,
    `date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
