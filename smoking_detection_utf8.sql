-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: smoking_detection
-- ------------------------------------------------------
-- Server version	9.5.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'f6c6198f-b0dd-11f0-8a80-50bbb553ba1d:1-3827';

--
-- Table structure for table `cameras`
--

DROP TABLE IF EXISTS `cameras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cameras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `camera_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `camera_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `camera_source` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_online` tinyint(1) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `api_key` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `confidence_threshold` float DEFAULT NULL,
  `iou_threshold` float DEFAULT NULL,
  `enable_alert` tinyint(1) DEFAULT NULL,
  `enable_screenshot` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_cameras_api_key` (`api_key`),
  KEY `user_id` (`user_id`),
  KEY `ix_cameras_id` (`id`),
  CONSTRAINT `cameras_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cameras`
--

LOCK TABLES `cameras` WRITE;
/*!40000 ALTER TABLE `cameras` DISABLE KEYS */;
INSERT INTO `cameras` VALUES (2,1,'辦公室攝影機','usb','0','1樓大廳',1,0,'2025-10-31 15:53:47','Ye2-NmHa9uIPX87B7pybBcP0CJsVffO5sMXQmvcA43A',0.7,0.5,1,1,'2025-10-24 22:49:30','2025-10-31 15:53:47'),(3,1,'本地端(PC)','local','','',1,0,'2025-10-30 14:23:24','zfFB9aQO2FcYLUm4nfqIOhSb-XA79_TzcJzpEFiiAC4',0.7,0.5,1,1,'2025-10-24 23:30:04','2025-10-30 14:23:24'),(7,1,'中華路 (學校後門) 攝影機','usb','','馬路旁',1,0,'2025-11-02 19:42:44','kdBvfhY9nnjwJeH5pEoqGBCvYZnjuBe4MD5r4AYWXrc',0.7,0.5,1,1,'2025-11-02 19:42:18','2025-11-02 19:42:44');
/*!40000 ALTER TABLE `cameras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detections`
--

DROP TABLE IF EXISTS `detections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `camera_id` int NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `has_person` tinyint(1) DEFAULT NULL,
  `has_cigarette` tinyint(1) DEFAULT NULL,
  `is_smoking` tinyint(1) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `screenshot_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detection_details` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `camera_id` (`camera_id`),
  KEY `ix_detections_timestamp` (`timestamp`),
  KEY `ix_detections_id` (`id`),
  CONSTRAINT `detections_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `detections_ibfk_2` FOREIGN KEY (`camera_id`) REFERENCES `cameras` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1062 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detections`
--

LOCK TABLES `detections` WRITE;
/*!40000 ALTER TABLE `detections` DISABLE KEYS */;
INSERT INTO `detections` VALUES (1058,1,2,'2025-10-31 15:51:15',1,1,1,0.868743,'violation_2_20251031_155115.jpg','[{\"x1\": 318.7498779296875, \"y1\": 193.4195556640625, \"x2\": 479.7135009765625, \"y2\": 412.26153564453125, \"confidence\": 0.8687431216239929, \"class\": 1, \"label\": \"person\"}, {\"x1\": 310.30450439453125, \"y1\": 319.7719421386719, \"x2\": 374.7506103515625, \"y2\": 358.2307434082031, \"confidence\": 0.8584542274475098, \"class\": 0, \"label\": \"cigarette\"}]','2025-10-31 15:51:15'),(1059,1,2,'2025-10-31 15:53:44',1,1,1,0.887131,'violation_2_20251031_155344.jpg','[{\"x1\": 292.15313720703125, \"y1\": 192.9539337158203, \"x2\": 447.90191650390625, \"y2\": 399.88360595703125, \"confidence\": 0.8871310949325562, \"class\": 1, \"label\": \"person\"}, {\"x1\": 344.754638671875, \"y1\": 335.81427001953125, \"x2\": 374.63726806640625, \"y2\": 396.82806396484375, \"confidence\": 0.8196520805358887, \"class\": 0, \"label\": \"cigarette\"}]','2025-10-31 15:53:44'),(1060,1,7,'2025-11-02 19:42:29',1,1,1,0.7,'violation_7_20251102_194229.jpg','[{\"x1\": 240.36558532714844, \"y1\": 210.973388671875, \"x2\": 389.2730712890625, \"y2\": 408.54888916015625, \"confidence\": 0.9019942879676819, \"class\": 1, \"label\": \"person\"}, {\"x1\": 285.5906982421875, \"y1\": 344.6099853515625, \"x2\": 304.3912353515625, \"y2\": 380.1968994140625, \"confidence\": 0.8051809668540955, \"class\": 0, \"label\": \"cigarette\"}]','2025-11-02 19:42:29'),(1061,1,7,'2025-11-02 19:42:39',1,1,1,0.8,'violation_7_20251102_194239.jpg','[{\"x1\": 214.7854461669922, \"y1\": 198.89898681640625, \"x2\": 388.63336181640625, \"y2\": 411.773681640625, \"confidence\": 0.8189457058906555, \"class\": 1, \"label\": \"person\"}, {\"x1\": 208.05950927734375, \"y1\": 317.2918701171875, \"x2\": 255.9140625, \"y2\": 340.3363037109375, \"confidence\": 0.8012635707855225, \"class\": 0, \"label\": \"cigarette\"}]','2025-11-02 19:42:39');
/*!40000 ALTER TABLE `detections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hashed_password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@example.com','$2b$12$oXQ8fwYHXoyBQRUYcozPn.KiRusuJFCtZhhsWu6XKYsdMYCiqWDLe','系統管理員',1,0,'2025-10-24 22:33:58','2025-10-24 22:33:58'),(2,'lynn','bkzero0000@gmail.com','$2b$12$BlfvW3agEcrASsnragmGh.AM6didPqLF7Lp0mS3blUxvUqR/g9CdC','廖00',1,0,'2025-10-30 15:29:15','2025-10-30 15:29:15'),(3,'張XX','b.kzero0000@gmail.com','$2b$12$edExVkN8TkTVLUuY2PMeieV/DMAgpUPE3tisB/FBy5f5V7BxG0mXu','',1,0,'2025-10-31 16:54:38','2025-10-31 16:54:38');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-12 13:49:11
