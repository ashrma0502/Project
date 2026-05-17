-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: flight_booking
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `airline`
--

DROP TABLE IF EXISTS `airline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airline` (
  `airline_id` varchar(50) NOT NULL,
  `airline_name` varchar(50) DEFAULT NULL,
  `model_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`airline_id`),
  KEY `model_id` (`model_id`),
  CONSTRAINT `airline_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `model` (`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airline`
--

LOCK TABLES `airline` WRITE;
/*!40000 ALTER TABLE `airline` DISABLE KEYS */;
INSERT INTO `airline` VALUES ('A1','IndiGo','M2'),('A10','Lufthansa','M14'),('A11','Delta','M12'),('A12','United','M13'),('A13','British Airways','M10'),('A14','Singapore Airlines','M11'),('A15','Etihad','M15'),('A2','Air India','M3'),('A3','SpiceJet','M1'),('A4','Vistara','M4'),('A5','GoAir','M5'),('A6','AirAsia','M6'),('A7','Alliance Air','M7'),('A8','Emirates','M3'),('A9','Qatar Airways','M11');
/*!40000 ALTER TABLE `airline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `airport`
--

DROP TABLE IF EXISTS `airport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `airport` (
  `airport_id` varchar(50) NOT NULL,
  `airport_name` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`airport_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `airport`
--

LOCK TABLES `airport` WRITE;
/*!40000 ALTER TABLE `airport` DISABLE KEYS */;
INSERT INTO `airport` VALUES ('AP1','IGI Airport','Delhi','India'),('AP10','Changi','Singapore','Singapore'),('AP11','Doha Airport','Doha','Qatar'),('AP12','Frankfurt','Frankfurt','Germany'),('AP13','Narita','Tokyo','Japan'),('AP14','Sydney Airport','Sydney','Australia'),('AP15','Toronto Pearson','Toronto','Canada'),('AP2','CSMIA','Mumbai','India'),('AP3','Kempegowda','Bangalore','India'),('AP4','Chennai Airport','Chennai','India'),('AP5','Kolkata Airport','Kolkata','India'),('AP6','Heathrow','London','UK'),('AP7','JFK','New York','USA'),('AP8','LAX','Los Angeles','USA'),('AP9','Dubai Intl','Dubai','UAE');
/*!40000 ALTER TABLE `airport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `booking_id` varchar(50) NOT NULL,
  `username` varchar(20) DEFAULT NULL,
  `flight_id` varchar(50) DEFAULT NULL,
  `amount` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `username` (`username`),
  KEY `flight_id` (`flight_id`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`),
  CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`flight_id`) REFERENCES `flight` (`flight_id`),
  CONSTRAINT `chk_amount` CHECK ((`amount` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES ('B1','user1','F1',5500.00),('B10','user10','F10',11000.00),('B11','user11','F11',12100.00),('B12','user12','F12',13200.00),('B13','user13','F13',10450.00),('B14','user14','F14',11550.00),('B15','user15','F15',12650.00),('B2','user2','F2',6600.00),('B3','user3','F3',6050.00),('B4','user4','F4',7700.00),('B5','user5','F5',4950.00),('B6','user6','F6',8800.00),('B7','user7','F7',8250.00),('B8','user8','F8',9900.00),('B9','user9','F9',7150.00);
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight` (
  `flight_id` varchar(50) NOT NULL,
  `airline_id` varchar(50) DEFAULT NULL,
  `airport_id` varchar(50) DEFAULT NULL,
  `arrival_time` datetime DEFAULT NULL,
  `departure_time` datetime DEFAULT NULL,
  `flight_name` varchar(50) DEFAULT NULL,
  `destination` varchar(50) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`flight_id`),
  KEY `airline_id` (`airline_id`),
  KEY `airport_id` (`airport_id`),
  CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`airline_id`) REFERENCES `airline` (`airline_id`),
  CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`airport_id`) REFERENCES `airport` (`airport_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight`
--

LOCK TABLES `flight` WRITE;
/*!40000 ALTER TABLE `flight` DISABLE KEYS */;
INSERT INTO `flight` VALUES ('F1','A1','AP1','2025-04-25 10:00:00','2025-04-25 07:00:00','Indigo101','Mumbai','Delhi'),('F10','A10','AP10','2025-04-26 18:00:00','2025-04-26 12:00:00','LH1010','Germany','India'),('F11','A11','AP11','2025-04-27 10:00:00','2025-04-27 06:00:00','DL111','USA','Qatar'),('F12','A12','AP12','2025-04-27 12:00:00','2025-04-27 07:00:00','UA222','USA','Germany'),('F13','A13','AP13','2025-04-27 14:00:00','2025-04-27 09:00:00','BA333','UK','Japan'),('F14','A14','AP14','2025-04-27 16:00:00','2025-04-27 10:00:00','SQ444','Singapore','Australia'),('F15','A15','AP15','2025-04-27 18:00:00','2025-04-27 12:00:00','EY555','UAE','Canada'),('F2','A2','AP2','2025-04-25 12:00:00','2025-04-25 08:00:00','AI202','Delhi','Mumbai'),('F3','A3','AP3','2025-04-25 14:00:00','2025-04-25 09:00:00','SJ303','Chennai','Bangalore'),('F4','A4','AP4','2025-04-25 16:00:00','2025-04-25 11:00:00','VS404','Delhi','Chennai'),('F5','A5','AP5','2025-04-25 18:00:00','2025-04-25 13:00:00','GA505','Kolkata','Delhi'),('F6','A6','AP6','2025-04-26 10:00:00','2025-04-26 06:00:00','AA606','London','Delhi'),('F7','A7','AP7','2025-04-26 12:00:00','2025-04-26 07:00:00','AL707','NY','Delhi'),('F8','A8','AP8','2025-04-26 14:00:00','2025-04-26 09:00:00','EM808','Dubai','USA'),('F9','A9','AP9','2025-04-26 16:00:00','2025-04-26 10:00:00','QA909','Doha','India');
/*!40000 ALTER TABLE `flight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `model`
--

DROP TABLE IF EXISTS `model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model` (
  `model_id` varchar(50) NOT NULL,
  `model_name` varchar(50) DEFAULT NULL,
  `provider` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model`
--

LOCK TABLES `model` WRITE;
/*!40000 ALTER TABLE `model` DISABLE KEYS */;
INSERT INTO `model` VALUES ('M1','Boeing 737','Boeing'),('M10','A220','Airbus'),('M11','B787','Boeing'),('M12','B767','Boeing'),('M13','A319','Airbus'),('M14','A330','Airbus'),('M15','B737 MAX','Boeing'),('M2','A320','Airbus'),('M3','A380','Airbus'),('M4','B747','Boeing'),('M5','B777','Boeing'),('M6','A321','Airbus'),('M7','ATR72','ATR'),('M8','E190','Embraer'),('M9','CRJ700','Bombardier');
/*!40000 ALTER TABLE `model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `passenger`
--

DROP TABLE IF EXISTS `passenger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `passenger` (
  `passenger_id` varchar(50) NOT NULL,
  `payment_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`passenger_id`),
  KEY `payment_id` (`payment_id`),
  CONSTRAINT `passenger_ibfk_1` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`payment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `passenger`
--

LOCK TABLES `passenger` WRITE;
/*!40000 ALTER TABLE `passenger` DISABLE KEYS */;
INSERT INTO `passenger` VALUES ('PS1','P1'),('PS10','P10'),('PS11','P11'),('PS12','P12'),('PS13','P13'),('PS14','P14'),('PS15','P15'),('PS2','P2'),('PS3','P3'),('PS4','P4'),('PS5','P5'),('PS6','P6'),('PS7','P7'),('PS8','P8'),('PS9','P9');
/*!40000 ALTER TABLE `passenger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `payment_id` varchar(50) NOT NULL,
  `payment_status` varchar(50) DEFAULT NULL,
  `booking_id` varchar(50) DEFAULT NULL,
  `payment_method` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`booking_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES ('P1','SUCCESS','B1','1'),('P10','SUCCESS','B10','1'),('P11','SUCCESS','B11','1'),('P12','FAILED','B12','0'),('P13','SUCCESS','B13','1'),('P14','SUCCESS','B14','1'),('P15','SUCCESS','B15','1'),('P2','SUCCESS','B2','1'),('P3','FAILED','B3','0'),('P4','SUCCESS','B4','1'),('P5','SUCCESS','B5','1'),('P6','FAILED','B6','0'),('P7','SUCCESS','B7','1'),('P8','SUCCESS','B8','1'),('P9','FAILED','B9','0');
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `username` varchar(20) NOT NULL,
  `email` varchar(30) DEFAULT NULL,
  `phone_number` bigint DEFAULT NULL,
  `pancard_id` varchar(20) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('user1','updated_user1@mail.com',9876543210,'PAN001',NULL),('user10','u10@mail.com',9876543219,'PAN010',NULL),('user11','u11@mail.com',9876543220,'PAN011',NULL),('user12','u12@mail.com',9876543221,'PAN012',NULL),('user13','u13@mail.com',9876543222,'PAN013',NULL),('user14','u14@mail.com',9876543223,'PAN014',NULL),('user15','u15@mail.com',9876543224,'PAN015',NULL),('user2','u2@mail.com',9876543211,'PAN002',NULL),('user3','u3@mail.com',9876543212,'PAN003',NULL),('user4','u4@mail.com',9876543213,'PAN004',NULL),('user5','u5@mail.com',9876543214,'PAN005',NULL),('user6','u6@mail.com',9876543215,'PAN006',NULL),('user7','u7@mail.com',9876543216,'PAN007',NULL),('user8','u8@mail.com',9876543217,'PAN008',NULL),('user9','u9@mail.com',9876543218,'PAN009',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-24 19:23:57
