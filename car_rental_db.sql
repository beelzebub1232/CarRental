-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jul 17, 2025 at 06:15 AM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `car_rental_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
CREATE TABLE IF NOT EXISTS `bookings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `vehicle_id` int NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `discount_applied` decimal(10,2) DEFAULT '0.00',
  `loyalty_token_used` decimal(10,2) DEFAULT '0.00',
  `status` enum('pending','approved','paid','completed','rejected','cancelled') NOT NULL,
  `booking_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `vehicle_id` (`vehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `user_id`, `vehicle_id`, `start_date`, `end_date`, `total_price`, `discount_applied`, `loyalty_token_used`, `status`, `booking_date`) VALUES
(6, 2, 86, '2025-07-16 00:05:00', '2025-07-17 00:05:00', 9120.00, 0.00, 0.00, 'paid', '2025-07-14 18:35:36'),
(7, 2, 86, '2025-07-16 00:09:00', '2025-07-17 00:09:00', 9120.00, 0.00, 0.00, 'paid', '2025-07-14 18:39:59'),
(8, 2, 95, '2025-07-16 15:08:00', '2025-07-17 07:06:00', 23950.00, 0.00, 0.00, 'paid', '2025-07-14 19:37:07'),
(9, 2, 55, '2025-07-16 01:24:00', '2025-07-17 01:24:00', 9120.00, 0.00, 0.00, 'cancelled', '2025-07-14 19:54:31'),
(10, 2, 179, '2025-07-16 17:56:00', '2025-07-17 18:57:00', 70827.70, 0.00, 0.00, 'pending', '2025-07-14 23:25:16'),
(11, 4, 272, '2025-07-16 18:19:00', '2025-07-17 18:19:00', 165891.83, 0.00, 0.00, 'rejected', '2025-07-14 23:56:07'),
(12, 4, 244, '2025-07-16 07:00:00', '2025-07-17 11:00:00', 64400.00, 0.00, 0.00, 'completed', '2025-07-14 23:58:13'),
(13, 4, 313, '2025-07-16 18:36:00', '2025-07-16 20:38:00', 87842.03, 0.00, 0.00, 'rejected', '2025-07-15 00:06:05'),
(14, 4, 303, '2025-07-15 09:05:00', '2025-07-17 20:05:00', 30400.00, 0.00, 0.00, 'completed', '2025-07-15 00:33:59'),
(15, 4, 334, '2025-07-18 06:46:00', '2025-07-25 06:46:00', 82460.00, 0.00, 0.00, 'completed', '2025-07-15 01:16:59'),
(16, 4, 334, '2025-07-16 09:47:00', '2025-07-18 09:47:00', 23560.00, 0.00, 0.00, 'completed', '2025-07-15 04:17:57'),
(17, 4, 334, '2025-07-16 21:14:00', '2025-07-17 21:14:00', 11780.00, 0.00, 0.00, 'paid', '2025-07-15 15:44:53'),
(18, 4, 334, '2025-07-16 21:36:00', '2025-07-17 21:36:00', 7657.00, 0.00, 4123.00, 'pending', '2025-07-15 16:06:16'),
(19, 4, 272, '2025-07-16 23:38:00', '2025-07-17 21:36:00', 7800.00, 0.00, 3220.00, 'rejected', '2025-07-15 16:07:05'),
(20, 4, 303, '2025-07-16 21:39:00', '2025-07-17 21:39:00', 11780.00, 0.00, 0.00, 'completed', '2025-07-15 16:10:04'),
(21, 4, 256, '2025-07-16 21:40:00', '2025-07-17 21:40:00', 7205.41, 0.00, 8294.59, 'completed', '2025-07-15 16:10:21'),
(22, 4, 310, '2025-07-16 21:50:00', '2025-07-18 21:50:00', 104811.00, 0.00, 589.00, 'completed', '2025-07-15 16:22:39'),
(23, 4, 309, '2025-07-16 21:52:00', '2025-07-24 21:52:00', 446400.00, 0.00, 0.00, 'pending', '2025-07-15 16:23:14'),
(24, 4, 303, '2025-07-17 12:53:00', '2025-07-18 21:53:00', 17499.73, 0.00, 360.27, 'completed', '2025-07-15 16:23:48'),
(25, 4, 303, '2025-07-16 22:01:00', '2025-07-18 22:01:00', 18319.45, 0.00, 5240.55, 'pending', '2025-07-15 16:31:13'),
(26, 4, 298, '2025-07-18 22:01:00', '2025-07-23 22:01:00', 49600.00, 0.00, 0.00, 'paid', '2025-07-15 16:31:37'),
(27, 4, 278, '2025-07-17 22:02:00', '2025-07-31 22:02:00', 780325.01, 0.00, 874.99, 'paid', '2025-07-15 16:33:01'),
(28, 4, 275, '2025-07-17 01:14:00', '2025-07-17 03:19:00', 6900.00, 0.00, 0.00, 'completed', '2025-07-15 19:45:17'),
(29, 4, 256, '2025-07-17 01:36:00', '2025-07-17 16:38:00', 8000.00, 0.00, 0.00, 'approved', '2025-07-15 20:06:52'),
(30, 4, 280, '2025-07-17 01:55:00', '2025-07-17 04:55:00', 4800.00, 0.00, 0.00, 'paid', '2025-07-15 20:26:21'),
(31, 4, 289, '2025-07-17 02:07:00', '2025-07-17 03:06:00', 480.00, 0.00, 0.00, 'completed', '2025-07-15 20:38:10');

-- --------------------------------------------------------

--
-- Table structure for table `customer_notifications`
--

DROP TABLE IF EXISTS `customer_notifications`;
CREATE TABLE IF NOT EXISTS `customer_notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `message` text NOT NULL,
  `type` varchar(50) DEFAULT 'info',
  `related_booking_id` int DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `related_booking_id` (`related_booking_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `customer_notifications`
--

INSERT INTO `customer_notifications` (`id`, `user_id`, `message`, `type`, `related_booking_id`, `is_read`, `created_at`) VALUES
(1, 4, 'Congratulations! You earned ₹1520.00 in loyalty rewards for your completed booking #14.', 'loyalty_reward', 14, 0, '2025-07-15 00:36:55'),
(2, 4, 'Congratulations! You earned ₹4123.00 in loyalty rewards for your completed booking #15.', 'loyalty_reward', 15, 0, '2025-07-15 01:18:20'),
(3, 4, 'Congratulations! You earned ₹1178.00 in loyalty rewards for your completed booking #16.', 'loyalty_reward', 16, 0, '2025-07-15 15:45:14'),
(4, 4, 'Congratulations! You earned ₹360.27 in loyalty rewards for your completed booking #21.', 'loyalty_reward', 21, 0, '2025-07-15 16:20:10'),
(5, 4, 'Congratulations! You earned ₹589.00 in loyalty rewards for your completed booking #20.', 'loyalty_reward', 20, 0, '2025-07-15 16:20:13'),
(6, 4, 'Congratulations! You earned ₹874.99 in loyalty rewards for your completed booking #24.', 'loyalty_reward', 24, 0, '2025-07-15 16:30:38'),
(7, 4, 'Congratulations! You earned ₹5240.55 in loyalty rewards for your completed booking #22.', 'loyalty_reward', 22, 0, '2025-07-15 16:30:40'),
(8, 4, 'Congratulations! You earned ₹345.00 in loyalty rewards for your completed booking #28.', 'loyalty_reward', 28, 0, '2025-07-15 19:46:31'),
(9, 4, 'Congratulations! You earned ₹24.00 in loyalty rewards for your completed booking #31.', 'loyalty_reward', 31, 0, '2025-07-15 20:39:54');

-- --------------------------------------------------------

--
-- Table structure for table `discounts`
--

DROP TABLE IF EXISTS `discounts`;
CREATE TABLE IF NOT EXISTS `discounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `discount_percentage` decimal(5,2) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `vehicle_id` int DEFAULT NULL,
  `vehicle_type` varchar(50) DEFAULT NULL,
  `usage_limit` int DEFAULT '0',
  `times_used` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `description` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `vehicle_id` (`vehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `discounts`
--

INSERT INTO `discounts` (`id`, `code`, `discount_percentage`, `start_date`, `end_date`, `vehicle_id`, `vehicle_type`, `usage_limit`, `times_used`, `is_active`, `description`, `created_at`) VALUES
(1, 'WELCOME20', 20.00, '2024-01-01', '2024-12-31', NULL, NULL, 100, 0, 1, NULL, '2025-07-13 11:10:45'),
(2, 'LUXURY50', 50.00, '2024-01-01', '2024-12-31', NULL, 'Luxury SUV', 20, 0, 1, NULL, '2025-07-13 11:10:45'),
(3, 'ELECTRIC15', 15.00, '2024-01-01', '2024-12-31', NULL, 'Electric', 50, 0, 1, NULL, '2025-07-13 11:10:45');

-- --------------------------------------------------------

--
-- Table structure for table `loyalty_tokens`
--

DROP TABLE IF EXISTS `loyalty_tokens`;
CREATE TABLE IF NOT EXISTS `loyalty_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token_value` decimal(10,2) NOT NULL,
  `is_redeemed` tinyint(1) DEFAULT '0',
  `issued_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expiry_date` timestamp NULL DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `loyalty_tokens`
--

INSERT INTO `loyalty_tokens` (`id`, `user_id`, `token_value`, `is_redeemed`, `issued_date`, `expiry_date`, `description`) VALUES
(16, 4, 360.27, 1, '2025-07-15 16:20:10', '2026-07-15 16:20:11', 'Earned from completed booking #21'),
(17, 4, 589.00, 1, '2025-07-15 16:20:13', '2026-07-15 16:20:13', 'Earned from completed booking #20'),
(18, 4, 874.99, 1, '2025-07-15 16:30:38', '2026-07-15 16:30:38', 'Earned from completed booking #24'),
(19, 4, 5240.55, 1, '2025-07-15 16:30:40', '2026-07-15 16:30:41', 'Earned from completed booking #22'),
(20, 4, 345.00, 0, '2025-07-15 19:46:31', '2026-07-15 19:46:32', 'Earned from completed booking #28'),
(21, 4, 24.00, 0, '2025-07-15 20:39:54', '2026-07-15 20:39:54', 'Earned from completed booking #31');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
CREATE TABLE IF NOT EXISTS `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) DEFAULT 'success',
  `method` varchar(50) DEFAULT 'dummy',
  `reference` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_id` (`booking_id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`id`, `booking_id`, `user_id`, `amount`, `payment_date`, `status`, `method`, `reference`) VALUES
(4, 6, 2, 9120.00, '2025-07-14 18:37:04', 'success', 'dummy', NULL),
(3, 5, 2, 9120.00, '2025-07-14 18:32:18', 'success', 'dummy', NULL),
(5, 8, 2, 23950.00, '2025-07-14 19:47:30', 'success', 'dummy', NULL),
(6, 7, 2, 9120.00, '2025-07-14 19:53:08', 'success', 'dummy', NULL),
(7, 9, 2, 9120.00, '2025-07-14 20:13:01', 'success', 'dummy', NULL),
(8, 12, 4, 64400.00, '2025-07-14 23:59:34', 'success', 'dummy', NULL),
(9, 14, 4, 30400.00, '2025-07-15 00:36:39', 'success', 'dummy', NULL),
(10, 15, 4, 82460.00, '2025-07-15 01:17:53', 'success', 'dummy', NULL),
(11, 16, 4, 23560.00, '2025-07-15 05:34:55', 'success', 'dummy', NULL),
(12, 17, 4, 11780.00, '2025-07-15 15:45:26', 'success', 'dummy', NULL),
(13, 21, 4, 7205.41, '2025-07-15 16:18:49', 'success', 'dummy', NULL),
(14, 20, 4, 11780.00, '2025-07-15 16:18:54', 'success', 'dummy', NULL),
(15, 24, 4, 17499.73, '2025-07-15 16:29:34', 'success', 'dummy', NULL),
(16, 22, 4, 104811.00, '2025-07-15 16:29:41', 'success', 'dummy', NULL),
(17, 27, 4, 780325.01, '2025-07-15 16:43:08', 'success', 'dummy', NULL),
(18, 26, 4, 49600.00, '2025-07-15 18:59:26', 'success', 'dummy', NULL),
(19, 28, 4, 6900.00, '2025-07-15 19:46:07', 'success', 'dummy', NULL),
(20, 30, 4, 4800.00, '2025-07-15 20:35:53', 'success', 'dummy', NULL),
(21, 31, 4, 480.00, '2025-07-15 20:39:25', 'success', 'dummy', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `pricing_rules`
--

DROP TABLE IF EXISTS `pricing_rules`;
CREATE TABLE IF NOT EXISTS `pricing_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_type` enum('time_peak','demand_location','demand_car_type','demand_proximity') NOT NULL,
  `vehicle_type` varchar(50) DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `peak_start_time` time DEFAULT NULL,
  `peak_end_time` time DEFAULT NULL,
  `ramp_up_minutes` int DEFAULT '0',
  `cool_down_minutes` int DEFAULT '0',
  `modifier_percentage` decimal(5,2) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `pricing_rules`
--

INSERT INTO `pricing_rules` (`id`, `rule_type`, `vehicle_type`, `location_id`, `peak_start_time`, `peak_end_time`, `ramp_up_minutes`, `cool_down_minutes`, `modifier_percentage`, `description`, `is_active`, `created_at`) VALUES
(1, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-13 11:10:45'),
(2, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-13 11:10:45'),
(3, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-13 11:10:45'),
(4, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-13 20:56:35'),
(5, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-13 20:56:35'),
(6, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-13 20:56:35'),
(7, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-13 20:56:47'),
(8, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-13 20:56:47'),
(9, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-13 20:56:47'),
(10, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-13 21:25:39'),
(11, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-13 21:25:39'),
(12, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-13 21:25:39'),
(13, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-13 22:00:03'),
(14, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-13 22:00:03'),
(15, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-13 22:00:03'),
(16, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-13 22:07:11'),
(17, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-13 22:07:11'),
(18, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-13 22:07:11'),
(19, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 17:41:38'),
(20, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 17:41:38'),
(21, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 17:41:38'),
(22, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 23:02:14'),
(23, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 23:02:14'),
(24, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 23:02:14'),
(25, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 23:18:37'),
(26, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 23:18:37'),
(27, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 23:18:37'),
(28, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 23:27:12'),
(29, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 23:27:12'),
(30, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 23:27:12'),
(31, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 23:45:37'),
(32, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 23:45:37'),
(33, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 23:45:37'),
(34, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 23:48:22'),
(35, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 23:48:22'),
(36, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 23:48:22'),
(37, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-14 23:49:41'),
(38, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-14 23:49:41'),
(39, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-14 23:49:41'),
(40, 'time_peak', NULL, NULL, '17:00:00', '19:00:00', 30, 30, 25.00, 'Evening peak hours', 1, '2025-07-15 00:04:14'),
(41, 'demand_car_type', 'Luxury SUV', NULL, NULL, NULL, 0, 0, 15.00, 'High demand for luxury SUVs', 1, '2025-07-15 00:04:14'),
(42, 'demand_car_type', 'Electric', NULL, NULL, NULL, 0, 0, 10.00, 'Eco-friendly premium', 1, '2025-07-15 00:04:14');

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
CREATE TABLE IF NOT EXISTS `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `user_id` int NOT NULL,
  `rating` int NOT NULL,
  `comment` text,
  `recommend` enum('yes','maybe','no') DEFAULT NULL,
  `condition_rating` int DEFAULT NULL,
  `service_rating` int DEFAULT NULL,
  `value_rating` int DEFAULT NULL,
  `review_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `booking_id` (`booking_id`),
  KEY `user_id` (`user_id`)
) ;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `booking_id`, `user_id`, `rating`, `comment`, `recommend`, `condition_rating`, `service_rating`, `value_rating`, `review_date`) VALUES
(1, 15, 4, 5, 'Test review', 'no', NULL, NULL, NULL, '2025-07-15 19:41:16'),
(3, 16, 4, 5, 'this is a test one', 'maybe', 3, 3, 5, '2025-07-15 19:41:07'),
(4, 31, 4, 5, 'Test Review 3', 'yes', 2, 4, 5, '2025-07-15 20:40:25');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `role` enum('customer','admin') NOT NULL DEFAULT 'customer',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `full_name`, `role`, `created_at`) VALUES
(1, 'admin@carrental.com', 'admin123', 'Admin User', 'admin', '2025-07-13 11:10:45'),
(4, 'test@gmail.com', '123123123', 'puffs', 'customer', '2025-07-14 23:35:27');

-- --------------------------------------------------------

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
CREATE TABLE IF NOT EXISTS `vehicles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `make` varchar(50) NOT NULL,
  `model` varchar(50) NOT NULL,
  `year` int NOT NULL,
  `type` varchar(50) NOT NULL,
  `base_price` decimal(10,2) NOT NULL,
  `availability` tinyint(1) DEFAULT '1',
  `status` enum('available','unavailable','maintenance') DEFAULT 'available',
  `pickup_location_lat` decimal(10,8) DEFAULT NULL,
  `pickup_location_lng` decimal(11,8) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=336 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `vehicles`
--

INSERT INTO `vehicles` (`id`, `make`, `model`, `year`, `type`, `base_price`, `availability`, `status`, `pickup_location_lat`, `pickup_location_lng`, `image_url`, `created_at`) VALUES
(335, 'puffs', 'nais', 2021, 'Electric Sedan', 1092.00, 1, 'available', 99.99999999, 999.99999999, 'nais.jpeg', '2025-07-15 00:42:07'),
(333, 'Tata', 'Ace', 2023, 'Commercial', 350.00, 1, 'available', 10.01670000, 76.30760000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-15 00:04:14'),
(334, 'Ashok Leyland', 'Dost', 2023, 'Commercial', 380.00, 1, 'available', 10.02560000, 76.32450000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-15 00:04:14'),
(332, 'Mahindra', 'Bolero', 2023, 'Commercial', 400.00, 1, 'available', 10.03010000, 76.31980000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-15 00:04:14'),
(331, 'Maruti', 'Baleno', 2023, 'Hatchback', 310.00, 1, 'available', 10.02780000, 76.31230000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-15 00:04:14'),
(329, 'Hyundai', 'i20', 2023, 'Hatchback', 320.00, 1, 'available', 10.03340000, 76.30890000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-15 00:04:14'),
(330, 'Tata', 'Punch', 2023, 'Hatchback', 280.00, 1, 'available', 10.01560000, 76.32180000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-15 00:04:14'),
(328, 'Maruti', 'Swift', 2023, 'Hatchback', 300.00, 1, 'available', 10.01890000, 76.31450000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-15 00:04:14'),
(327, 'Kia', 'Seltos', 2023, 'SUV', 620.00, 1, 'available', 10.02450000, 76.32010000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-15 00:04:14'),
(320, 'Hyundai', 'Verna', 2023, 'Sedan', 480.00, 1, 'available', 10.01780000, 76.32450000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-15 00:04:14'),
(321, 'Toyota', 'Camry', 2023, 'Sedan', 800.00, 1, 'available', 10.02560000, 76.31090000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-15 00:04:14'),
(322, 'Skoda', 'Rapid', 2023, 'Sedan', 550.00, 1, 'available', 10.03890000, 76.31760000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-15 00:04:14'),
(323, 'Mahindra', 'XUV700', 2023, 'SUV', 700.00, 1, 'available', 10.01340000, 76.30870000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-15 00:04:14'),
(324, 'Tata', 'Harrier', 2023, 'SUV', 650.00, 1, 'available', 10.02980000, 76.32340000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-15 00:04:14'),
(325, 'MG', 'Hector', 2023, 'SUV', 750.00, 1, 'available', 10.02010000, 76.31650000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-15 00:04:14'),
(326, 'Hyundai', 'Creta', 2023, 'SUV', 600.00, 1, 'available', 10.03670000, 76.30540000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-15 00:04:14'),
(299, 'Tata', 'Punch', 2023, 'Hatchback', 280.00, 1, 'available', 10.01560000, 76.32180000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:49:41'),
(319, 'Maruti', 'Ciaz', 2023, 'Sedan', 450.00, 1, 'available', 10.03120000, 76.30670000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-15 00:04:14'),
(318, 'Honda', 'City', 2023, 'Sedan', 500.00, 1, 'available', 10.02230000, 76.31870000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-15 00:04:14'),
(317, 'Tata', 'Nexon EV', 2023, 'Electric SUV', 600.00, 1, 'available', 10.03560000, 76.31230000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-15 00:04:14'),
(316, 'MG', 'ZS EV', 2023, 'Electric SUV', 800.00, 1, 'available', 10.01670000, 76.31560000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-15 00:04:14'),
(315, 'Tesla', 'Model Y', 2023, 'Electric SUV', 1400.00, 1, 'available', 10.02890000, 76.30980000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-15 00:04:14'),
(314, 'Tesla', 'Model 3', 2023, 'Electric Sedan', 1200.00, 1, 'available', 10.01450000, 76.32120000, 'https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg', '2025-07-15 00:04:14'),
(313, 'Jaguar', 'F-Pace', 2023, 'Premium SUV', 1900.00, 1, 'available', 10.03760000, 76.30450000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-15 00:04:14'),
(312, 'Volvo', 'XC60', 2023, 'Premium SUV', 1500.00, 1, 'available', 10.02120000, 76.31980000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-15 00:04:14'),
(311, 'Audi', 'Q5', 2023, 'Premium SUV', 1600.00, 1, 'available', 10.03450000, 76.30780000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-15 00:04:14'),
(310, 'Mercedes-Benz', 'GLC', 2023, 'Premium SUV', 1700.00, 1, 'available', 10.01980000, 76.31340000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-15 00:04:14'),
(309, 'BMW', 'X5', 2023, 'Premium SUV', 1800.00, 1, 'available', 10.02670000, 76.30230000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-15 00:04:14'),
(308, 'Lexus', 'LX', 2023, 'Luxury SUV', 2600.00, 1, 'available', 10.03210000, 76.31670000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-15 00:04:14'),
(307, 'Range Rover', 'Sport', 2023, 'Luxury SUV', 2800.00, 1, 'available', 10.01560000, 76.30890000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-15 00:04:14'),
(306, 'Audi', 'A8', 2023, 'Luxury Sedan', 2300.00, 1, 'available', 10.02980000, 76.31450000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-15 00:04:14'),
(305, 'BMW', '7 Series', 2023, 'Luxury Sedan', 2200.00, 1, 'available', 10.01870000, 76.30560000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-15 00:04:14'),
(304, 'Mercedes-Benz', 'S-Class', 2023, 'Luxury Sedan', 2500.00, 1, 'available', 10.02340000, 76.31120000, 'https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg', '2025-07-15 00:04:14'),
(303, 'Ashok Leyland', 'Dost', 2023, 'Commercial', 380.00, 1, 'available', 10.02560000, 76.32450000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-14 23:49:41'),
(302, 'Tata', 'Ace', 2023, 'Commercial', 350.00, 1, 'available', 10.01670000, 76.30760000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-14 23:49:41'),
(301, 'Mahindra', 'Bolero', 2023, 'Commercial', 400.00, 1, 'available', 10.03010000, 76.31980000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-14 23:49:41'),
(300, 'Maruti', 'Baleno', 2023, 'Hatchback', 310.00, 1, 'available', 10.02780000, 76.31230000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:49:41'),
(298, 'Hyundai', 'i20', 2023, 'Hatchback', 320.00, 1, 'available', 10.03340000, 76.30890000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:49:41'),
(297, 'Maruti', 'Swift', 2023, 'Hatchback', 300.00, 1, 'available', 10.01890000, 76.31450000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:49:41'),
(296, 'Kia', 'Seltos', 2023, 'SUV', 620.00, 1, 'available', 10.02450000, 76.32010000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:49:41'),
(295, 'Hyundai', 'Creta', 2023, 'SUV', 600.00, 1, 'available', 10.03670000, 76.30540000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:49:41'),
(294, 'MG', 'Hector', 2023, 'SUV', 750.00, 1, 'available', 10.02010000, 76.31650000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:49:41'),
(293, 'Tata', 'Harrier', 2023, 'SUV', 650.00, 1, 'available', 10.02980000, 76.32340000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:49:41'),
(292, 'Mahindra', 'XUV700', 2023, 'SUV', 700.00, 1, 'available', 10.01340000, 76.30870000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:49:41'),
(291, 'Skoda', 'Rapid', 2023, 'Sedan', 550.00, 1, 'available', 10.03890000, 76.31760000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:49:41'),
(290, 'Toyota', 'Camry', 2023, 'Sedan', 800.00, 1, 'available', 10.02560000, 76.31090000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-14 23:49:41'),
(289, 'Hyundai', 'Verna', 2023, 'Sedan', 480.00, 1, 'available', 10.01780000, 76.32450000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:49:41'),
(288, 'Maruti', 'Ciaz', 2023, 'Sedan', 450.00, 1, 'available', 10.03120000, 76.30670000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:49:41'),
(287, 'Honda', 'City', 2023, 'Sedan', 500.00, 1, 'available', 10.02230000, 76.31870000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:49:41'),
(286, 'Tata', 'Nexon EV', 2023, 'Electric SUV', 600.00, 1, 'available', 10.03560000, 76.31230000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:49:41'),
(285, 'MG', 'ZS EV', 2023, 'Electric SUV', 800.00, 1, 'available', 10.01670000, 76.31560000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:49:41'),
(284, 'Tesla', 'Model Y', 2023, 'Electric SUV', 1400.00, 1, 'available', 10.02890000, 76.30980000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:49:41'),
(283, 'Tesla', 'Model 3', 2023, 'Electric Sedan', 1200.00, 1, 'available', 10.01450000, 76.32120000, 'https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg', '2025-07-14 23:49:41'),
(282, 'Jaguar', 'F-Pace', 2023, 'Premium SUV', 1900.00, 1, 'available', 10.03760000, 76.30450000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:49:41'),
(281, 'Volvo', 'XC60', 2023, 'Premium SUV', 1500.00, 1, 'maintenance', 10.02120000, 76.31980000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-14 23:49:41'),
(280, 'Audi', 'Q5', 2023, 'Premium SUV', 1600.00, 1, 'available', 10.03450000, 76.30780000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:49:41'),
(279, 'Mercedes-Benz', 'GLC', 2023, 'Premium SUV', 1700.00, 1, 'available', 10.01980000, 76.31340000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:49:41'),
(278, 'BMW', 'X5', 2023, 'Premium SUV', 1800.00, 1, 'available', 10.02670000, 76.30230000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:49:41'),
(277, 'Lexus', 'LX', 2023, 'Luxury SUV', 2600.00, 1, 'available', 10.03210000, 76.31670000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:49:41'),
(276, 'Range Rover', 'Sport', 2023, 'Luxury SUV', 2800.00, 1, 'available', 10.01560000, 76.30890000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-14 23:49:41'),
(275, 'Audi', 'A8', 2023, 'Luxury Sedan', 2300.00, 1, 'available', 10.02980000, 76.31450000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:49:41'),
(274, 'BMW', '7 Series', 2023, 'Luxury Sedan', 2200.00, 1, 'available', 10.01870000, 76.30560000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:49:41'),
(273, 'Mercedes-Benz', 'S-Class', 2023, 'Luxury Sedan', 2500.00, 1, 'available', 10.02340000, 76.31120000, 'https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg', '2025-07-14 23:49:41'),
(272, 'Ashok Leyland', 'Dost', 2023, 'Commercial', 380.00, 1, 'available', 10.02560000, 76.32450000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-14 23:48:22'),
(271, 'Tata', 'Ace', 2023, 'Commercial', 350.00, 1, 'available', 10.01670000, 76.30760000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-14 23:48:22'),
(270, 'Mahindra', 'Bolero', 2023, 'Commercial', 400.00, 1, 'available', 10.03010000, 76.31980000, 'https://images.pexels.com/photos/1118448/pexels-photo-1118448.jpeg', '2025-07-14 23:48:22'),
(269, 'Maruti', 'Baleno', 2023, 'Hatchback', 310.00, 1, 'available', 10.02780000, 76.31230000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:48:22'),
(268, 'Tata', 'Punch', 2023, 'Hatchback', 280.00, 1, 'available', 10.01560000, 76.32180000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:48:22'),
(267, 'Hyundai', 'i20', 2023, 'Hatchback', 320.00, 1, 'available', 10.03340000, 76.30890000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:48:22'),
(266, 'Maruti', 'Swift', 2023, 'Hatchback', 300.00, 1, 'available', 10.01890000, 76.31450000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:48:22'),
(265, 'Kia', 'Seltos', 2023, 'SUV', 620.00, 1, 'available', 10.02450000, 76.32010000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:48:22'),
(264, 'Hyundai', 'Creta', 2023, 'SUV', 600.00, 1, 'unavailable', 10.03670000, 76.30540000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:48:22'),
(263, 'MG', 'Hector', 2023, 'SUV', 750.00, 1, 'available', 10.02010000, 76.31650000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:48:22'),
(262, 'Tata', 'Harrier', 2023, 'SUV', 650.00, 1, 'available', 10.02980000, 76.32340000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:48:22'),
(261, 'Mahindra', 'XUV700', 2023, 'SUV', 700.00, 1, 'available', 10.01340000, 76.30870000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:48:22'),
(260, 'Skoda', 'Rapid', 2023, 'Sedan', 550.00, 1, 'available', 10.03890000, 76.31760000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:48:22'),
(259, 'Toyota', 'Camry', 2023, 'Sedan', 800.00, 1, 'available', 10.02560000, 76.31090000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-14 23:48:22'),
(258, 'Hyundai', 'Verna', 2023, 'Sedan', 480.00, 1, 'available', 10.01780000, 76.32450000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:48:22'),
(257, 'Maruti', 'Ciaz', 2023, 'Sedan', 450.00, 1, 'available', 10.03120000, 76.30670000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:48:22'),
(256, 'Honda', 'City', 2023, 'Sedan', 500.00, 1, 'available', 10.02230000, 76.31870000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:48:22'),
(255, 'Tata', 'Nexon EV', 2023, 'Electric SUV', 600.00, 1, 'available', 10.03560000, 76.31230000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:48:22'),
(254, 'MG', 'ZS EV', 2023, 'Electric SUV', 800.00, 1, 'available', 10.01670000, 76.31560000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:48:22'),
(253, 'Tesla', 'Model Y', 2023, 'Electric SUV', 1400.00, 1, 'available', 10.02890000, 76.30980000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:48:22'),
(252, 'Tesla', 'Model 3', 2023, 'Electric Sedan', 1200.00, 1, 'available', 10.01450000, 76.32120000, 'https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg', '2025-07-14 23:48:22'),
(251, 'Jaguar', 'F-Pace', 2023, 'Premium SUV', 1900.00, 1, 'available', 10.03760000, 76.30450000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:48:22'),
(250, 'Volvo', 'XC60', 2023, 'Premium SUV', 1500.00, 1, 'available', 10.02120000, 76.31980000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-14 23:48:22'),
(249, 'Audi', 'Q5', 2023, 'Premium SUV', 1600.00, 1, 'available', 10.03450000, 76.30780000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:48:22'),
(248, 'Mercedes-Benz', 'GLC', 2023, 'Premium SUV', 1700.00, 1, 'available', 10.01980000, 76.31340000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:48:22'),
(247, 'BMW', 'X5', 2023, 'Premium SUV', 1800.00, 1, 'available', 10.02670000, 76.30230000, 'https://images.pexels.com/photos/1335077/pexels-photo-1335077.jpeg', '2025-07-14 23:48:22'),
(246, 'Lexus', 'LX', 2023, 'Luxury SUV', 2600.00, 1, 'available', 10.03210000, 76.31670000, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg', '2025-07-14 23:48:22'),
(245, 'Range Rover', 'Sport', 2023, 'Luxury SUV', 2800.00, 1, 'available', 10.01560000, 76.30890000, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', '2025-07-14 23:48:22'),
(244, 'Audi', 'A8', 2023, 'Luxury Sedan', 2300.00, 1, 'available', 10.02980000, 76.31450000, 'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg', '2025-07-14 23:48:22'),
(243, 'BMW', '7 Series', 2023, 'Luxury Sedan', 2200.00, 1, 'available', 10.01870000, 76.30560000, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg', '2025-07-14 23:48:22'),
(242, 'Mercedes-Benz', 'S-Class', 2023, 'Luxury Sedan', 2500.00, 1, 'available', 10.02340000, 76.31120000, 'https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg', '2025-07-14 23:48:22');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
