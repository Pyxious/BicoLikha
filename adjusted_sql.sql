-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 16, 2026 at 11:45 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `bl_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `address`
--

CREATE TABLE `address` (
  `ADDRESS_ID` int(11) NOT NULL,
  `USER_ID` int(11) DEFAULT NULL,
  `ADDRESS_TYPE` varchar(50) DEFAULT NULL,
  `ADDRESS_PHONE_NUM` varchar(20) DEFAULT NULL,
  `ADDRESS_HOUSE_NUM` varchar(20) DEFAULT NULL,
  `ADDRESS_STREET` varchar(100) DEFAULT NULL,
  `ADDRESS_MUNICIPALITY` varchar(100) DEFAULT NULL,
  `ADDRESS_BRGY` varchar(100) DEFAULT NULL,
  `CUST_ZIPCODE` varchar(10) DEFAULT NULL,
  `LATITUDE` decimal(9,6) DEFAULT 13.139100,
  `LONGITUDE` decimal(9,6) DEFAULT 123.743800,
  `PROFILE_PIX` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `address`
--

INSERT INTO `address` (`ADDRESS_ID`, `USER_ID`, `ADDRESS_TYPE`, `ADDRESS_PHONE_NUM`, `ADDRESS_HOUSE_NUM`, `ADDRESS_STREET`, `ADDRESS_MUNICIPALITY`, `ADDRESS_BRGY`, `CUST_ZIPCODE`, `LATITUDE`, `LONGITUDE`, `PROFILE_PIX`) VALUES
(1, 3, 'Default', '09123456789', NULL, '1233454676', 'Legazpi ', '1231231', '123123', 13.139100, 123.743800, 'profile_pics/dmtry_2.png'),
(4, 11, 'Default', '09123457896', NULL, NULL, NULL, NULL, NULL, NULL, NULL, ''),
(5, 12, 'Default', '09123987594', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'profile_pics/loselose_2.png');

-- --------------------------------------------------------

--
-- Table structure for table `artist`
--

CREATE TABLE `artist` (
  `ARTIST_ID` int(11) NOT NULL,
  `ARTIST_NAME` varchar(255) DEFAULT NULL,
  `ARTIST_PHONE_NUM` varchar(20) DEFAULT NULL,
  `ARTIST_DESCRIPTION` text DEFAULT NULL,
  `ARTIST_SOCIAL_LINKS` text DEFAULT NULL,
  `ARTIST_IMAGE` varchar(255) DEFAULT NULL,
  `ARTIST_MUNICIPALITY` varchar(100) DEFAULT NULL,
  `ARTIST_BRGY` varchar(100) DEFAULT NULL,
  `ARTIST_ZIPCODE` varchar(10) DEFAULT NULL,
  `USER_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `artist`
--

INSERT INTO `artist` (`ARTIST_ID`, `ARTIST_NAME`, `ARTIST_PHONE_NUM`, `ARTIST_DESCRIPTION`, `ARTIST_SOCIAL_LINKS`, `ARTIST_IMAGE`, `ARTIST_MUNICIPALITY`, `ARTIST_BRGY`, `ARTIST_ZIPCODE`, `USER_ID`) VALUES
(25, 'Jess Lyn', '09123456789', 'Verified Artist', NULL, NULL, 'Legazpi', 'Albay', '4500', 3),
(26, 'Kristine Antegra', '09123987594', 'Verified Artist', NULL, NULL, 'Daraga', 'Poblacion', '4501', 12),
(27, 'Kirs Ten', '09123457896', 'Verified Artist', NULL, NULL, 'Legazpi', 'Bitano', '4500', 11);

-- --------------------------------------------------------

--
-- Table structure for table `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `action` text NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add artist', 7, 'add_artist'),
(26, 'Can change artist', 7, 'change_artist'),
(27, 'Can delete artist', 7, 'delete_artist'),
(28, 'Can view artist', 7, 'view_artist'),
(29, 'Can add artwork', 8, 'add_artwork'),
(30, 'Can change artwork', 8, 'change_artwork'),
(31, 'Can delete artwork', 8, 'delete_artwork'),
(32, 'Can view artwork', 8, 'view_artwork'),
(33, 'Can add cart', 9, 'add_cart'),
(34, 'Can change cart', 9, 'change_cart'),
(35, 'Can delete cart', 9, 'delete_cart'),
(36, 'Can view cart', 9, 'view_cart'),
(37, 'Can add category', 10, 'add_category'),
(38, 'Can change category', 10, 'change_category'),
(39, 'Can delete category', 10, 'delete_category'),
(40, 'Can view category', 10, 'view_category'),
(41, 'Can add payment', 11, 'add_payment'),
(42, 'Can change payment', 11, 'change_payment'),
(43, 'Can delete payment', 11, 'delete_payment'),
(44, 'Can view payment', 11, 'view_payment'),
(45, 'Can add review', 12, 'add_review'),
(46, 'Can change review', 12, 'change_review'),
(47, 'Can delete review', 12, 'delete_review'),
(48, 'Can view review', 12, 'view_review'),
(49, 'Can add order', 13, 'add_order'),
(50, 'Can change order', 13, 'change_order'),
(51, 'Can delete order', 13, 'delete_order'),
(52, 'Can view order', 13, 'view_order'),
(53, 'Can add like', 14, 'add_like'),
(54, 'Can change like', 14, 'change_like'),
(55, 'Can delete like', 14, 'delete_like'),
(56, 'Can view like', 14, 'view_like'),
(57, 'Can add address', 15, 'add_address'),
(58, 'Can change address', 15, 'change_address'),
(59, 'Can delete address', 15, 'delete_address'),
(60, 'Can view address', 15, 'view_address'),
(61, 'Can add order detail', 16, 'add_orderdetail'),
(62, 'Can change order detail', 16, 'change_orderdetail'),
(63, 'Can delete order detail', 16, 'delete_orderdetail'),
(64, 'Can view order detail', 16, 'view_orderdetail'),
(65, 'Can add cart item', 17, 'add_cartitem'),
(66, 'Can change cart item', 17, 'change_cartitem'),
(67, 'Can delete cart item', 17, 'delete_cartitem'),
(68, 'Can view cart item', 17, 'view_cartitem'),
(69, 'Can add notification', 18, 'add_notification'),
(70, 'Can change notification', 18, 'change_notification'),
(71, 'Can delete notification', 18, 'delete_notification'),
(72, 'Can view notification', 18, 'view_notification'),
(73, 'Can add audit log', 19, 'add_auditlog'),
(74, 'Can change audit log', 19, 'change_auditlog'),
(75, 'Can delete audit log', 19, 'delete_auditlog'),
(76, 'Can view audit log', 19, 'view_auditlog');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$600000$wgfOT8hOuFJhVBwEkoZO6p$xeOKBY+DK6hkK+A9E1SU4x51gRm2ypFtAhlwfeVZVbA=', NULL, 1, 'justin', '', '', 'vincealcayde2@gmail.com', 1, 1, '2026-04-15 18:06:49.842838'),
(2, 'pbkdf2_sha256$600000$7nbVq40El59uHEYvWfwbJc$HsxElMeJosjbLoSd4aRu3Pr36TOFO/57wJDAIyNDO4Q=', '2026-04-16 21:18:01.384349', 1, 'vince', 'Justin', 'Alcayde', 'vincealcayde@gmail.com', 1, 1, '2026-04-15 19:24:19.339945'),
(3, 'pbkdf2_sha256$600000$pK1pUk0mhwidCmOfDXDD1e$BS8XLfPRAed3QRYBjDiRKx/USWp4Flee4pGE9hfR1f8=', '2026-04-16 21:39:32.427217', 0, 'jesslyn@gmail.com', 'Jess', 'Lyn', 'jesslyn@gmail.com', 0, 1, '2026-04-15 20:21:37.375875'),
(11, 'pbkdf2_sha256$600000$PNU4WANke4CLsYCN3gxWz0$F0XW+64Q4i0MZeNQ/z6QBM0YaDjPSDq0Z8ZBlkUl498=', '2026-04-16 21:08:04.037758', 0, 'kirsten@gmail.com', 'Kirs', 'Ten', 'kirsten@gmail.com', 0, 1, '2026-04-16 21:08:03.746138'),
(12, 'pbkdf2_sha256$600000$9owoX5CmEjIGqRFmpLDimR$MozYP//FuOkWOl8gVrt60Wyp5dZw0W6Ni88uw+8XWnI=', '2026-04-16 21:42:11.392704', 0, 'kristine@gmail.com', 'Kristine', 'Antegra', 'kristine@gmail.com', 0, 1, '2026-04-16 21:08:32.353015');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `CART_ID` int(11) NOT NULL,
  `USER_ID` int(11) DEFAULT NULL,
  `TOTAL_ITEMS` int(11) DEFAULT 0,
  `DATE_CREATED` timestamp NOT NULL DEFAULT current_timestamp(),
  `DATE_DELETED` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cart`
--

INSERT INTO `cart` (`CART_ID`, `USER_ID`, `TOTAL_ITEMS`, `DATE_CREATED`, `DATE_DELETED`) VALUES
(1, 2, 0, '2026-04-15 12:11:48', NULL),
(2, 3, 0, '2026-04-15 12:21:37', NULL),
(5, 11, 0, '2026-04-16 13:08:04', NULL),
(6, 12, 0, '2026-04-16 13:08:32', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `id` int(11) NOT NULL,
  `CART_ID` int(11) NOT NULL,
  `PRODUCT_ID` int(11) NOT NULL,
  `QUANTITY` int(11) DEFAULT 1,
  `DATE_CREATED` timestamp NOT NULL DEFAULT current_timestamp(),
  `DATE_DELETED` timestamp NULL DEFAULT NULL,
  `is_selected` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cart_items`
--

INSERT INTO `cart_items` (`id`, `CART_ID`, `PRODUCT_ID`, `QUANTITY`, `DATE_CREATED`, `DATE_DELETED`, `is_selected`) VALUES
(18, 2, 13, 1, '2026-04-16 21:39:41', NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `category`
--

CREATE TABLE `category` (
  `CATEGORY_ID` int(11) NOT NULL,
  `CATEGORY_NAME` varchar(100) DEFAULT NULL,
  `CATEGORY_DESC` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `category`
--

INSERT INTO `category` (`CATEGORY_ID`, `CATEGORY_NAME`, `CATEGORY_DESC`) VALUES
(1, 'Oil Paintings', 'Traditional oil on canvas artworks focusing on landscapes and portraits.'),
(2, 'Sculptures', '3D artworks made from volcanic rock, wood, and recycled metals.'),
(3, 'Digital Art', 'Modern illustrations and conceptual art created digitally.'),
(4, 'Abaca Weaving', 'Traditional Bicolano textiles and hand-woven crafts.'),
(5, 'Pottery', 'Clay-fired ceramics and decorative earthenware.'),
(6, 'Watercolors', 'Light and fluid artworks using water-based pigments.'),
(7, 'Photography', 'Captured moments of Bicolano life, nature, and heritage.'),
(8, 'Mixed Media', 'Artworks combining different materials and techniques.');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(15, 'products', 'address'),
(7, 'products', 'artist'),
(8, 'products', 'artwork'),
(19, 'products', 'auditlog'),
(9, 'products', 'cart'),
(17, 'products', 'cartitem'),
(10, 'products', 'category'),
(14, 'products', 'like'),
(18, 'products', 'notification'),
(13, 'products', 'order'),
(16, 'products', 'orderdetail'),
(11, 'products', 'payment'),
(12, 'products', 'review'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-04-15 18:02:53.397440'),
(2, 'auth', '0001_initial', '2026-04-15 18:02:53.710505'),
(3, 'admin', '0001_initial', '2026-04-15 18:02:53.801924'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-04-15 18:02:53.807444'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-04-15 18:02:53.812453'),
(6, 'contenttypes', '0002_remove_content_type_name', '2026-04-15 18:02:53.857065'),
(7, 'auth', '0002_alter_permission_name_max_length', '2026-04-15 18:02:53.895746'),
(8, 'auth', '0003_alter_user_email_max_length', '2026-04-15 18:02:53.910345'),
(9, 'auth', '0004_alter_user_username_opts', '2026-04-15 18:02:53.916339'),
(10, 'auth', '0005_alter_user_last_login_null', '2026-04-15 18:02:53.949953'),
(11, 'auth', '0006_require_contenttypes_0002', '2026-04-15 18:02:53.954071'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2026-04-15 18:02:53.963805'),
(13, 'auth', '0008_alter_user_username_max_length', '2026-04-15 18:02:53.973185'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2026-04-15 18:02:53.982168'),
(15, 'auth', '0010_alter_group_name_max_length', '2026-04-15 18:02:53.992981'),
(16, 'auth', '0011_update_proxy_permissions', '2026-04-15 18:02:53.998626'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2026-04-15 18:02:54.008616'),
(18, 'products', '0001_initial', '2026-04-15 18:06:23.165092'),
(19, 'sessions', '0001_initial', '2026-04-15 18:06:23.167504'),
(20, 'products', '0002_alter_cartitem_id', '2026-04-15 19:46:29.765430'),
(21, 'products', '0003_address_latitude_address_longitude_and_more', '2026-04-15 20:58:44.781051'),
(22, 'products', '0004_address_profile_pix_artist_user_notification_and_more', '2026-04-16 20:42:48.202135'),
(23, 'products', '0005_address_delivery_fname_address_delivery_lname', '2026-04-16 21:03:14.326687');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('50gv1ovwx8hfy7kgdcxwn8fjmvbkikm7', '.eJxVjDEOgzAMAP_iuYpCEkLM2L1viGzHFNoKJAJT1b9XSAztene6N2TatzHvVdc8FejBweWXMclT50OUB833xcgyb-vE5kjMaau5LUVf17P9G4xUR-jBu0BSIkXvOHhqAorT1lKyqF1k6TpOqKmJ5Bp0KMI4WFbkQG1IQ4LPF9sdN9s:1wDU65:5Y1x0IQXJtJgQBhsuO0fVWfebwLQBfDHg8pbrQ2d3Ts', '2026-04-30 21:18:01.386548'),
('a46ghnbp5l9ggza2beff93tey4cpu00j', 'e30:1wD5yN:Td9HetbggeJ7z3Y_J25ljfUAcKDZzIHAZzq7BBE1Ce8', '2026-04-29 19:32:27.391387'),
('ivu35aodlxahfoqo7b7sz8ye3uepvi1l', '.eJxVjMsOgjAQAP9lz6ahlL44evcbml26a1FDEwon478bEg56nZnMGxLuW0l74zXNGUYwcPllhNOTl0PkBy73qqa6bOtM6kjUaZu61cyv69n-DQq2AiOId06YyHVDdNRjjsFrdIOxJCbmrHXH1noftKUgPSF6hyzcC4nGyPD5Au0DOKI:1wDU9f:Gx8xX-Mj6V049fRc6-BmulQ0eyU0VDqLRv6HxIr5-XI', '2026-04-30 21:21:43.193886'),
('vukxv7rc4tayli3haudih43bkrjrbzwv', '.eJxVjDkOwjAQAP-yNbJ8bNZ2Svq8wVof4ABypDipEH9HkVJAOzOaNwTetxr2XtYwZxhBabj8wsjpWdph8oPbfRFpads6R3Ek4rRdTEsur-vZ_g0q9wojkEwstbE6Z4rRZndTVCQbsoyGkdUQMRlLVrGXDj2jI0_JD8pjcqTg8wX4HDcW:1wDUTT:x6JdMTzc_WqoG0KQzGFGfYDqN1ZLuJff1R3A4IZnWjY', '2026-04-30 21:42:11.396097'),
('z01ot9oe3wkxe2vupylahn95t07nn48w', '.eJxVjMsOgjAQAP9lz6ahlL44evcbml26a1FDEwon478bEg56nZnMGxLuW0l74zXNGUYwcPllhNOTl0PkBy73qqa6bOtM6kjUaZu61cyv69n-DQq2AiOId06YyHVDdNRjjsFrdIOxJCbmrHXH1noftKUgPSF6hyzcC4nGyPD5Au0DOKI:1wDUCK:As5TGYO2TsZO6LzU3YTYzxl09SYzdffXRK-CZBt48Jc', '2026-04-30 21:24:28.017822');

-- --------------------------------------------------------

--
-- Table structure for table `likes`
--

CREATE TABLE `likes` (
  `LIKE_ID` int(11) NOT NULL,
  `USER_ID` int(11) DEFAULT NULL,
  `PRODUCT_ID` int(11) DEFAULT NULL,
  `DATE_LIKED` timestamp NOT NULL DEFAULT current_timestamp(),
  `DATE_DELETED` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `artist_id` int(11) NOT NULL,
  `message_text` text NOT NULL,
  `sender_role` varchar(50) NOT NULL,
  `status_update` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `order_id`, `artist_id`, `message_text`, `sender_role`, `status_update`, `is_read`, `timestamp`) VALUES
(7, 12, 25, 'New Order #BK-12. Please prepare the items.', 'Admin', NULL, 0, '2026-04-16 13:21:57'),
(8, 12, 25, 'ARTIST UPDATE: Status changed to Ready for Pickup.', 'Artist', 'Ready for Pickup', 0, '2026-04-16 13:22:08'),
(9, 12, 25, 'ARTIST UPDATE: Status changed to Item Picked Up.', 'Artist', 'Item Picked Up', 0, '2026-04-16 13:22:10'),
(11, 13, 25, 'New Order #BK-13. Please prepare the items.', 'Admin', NULL, 0, '2026-04-16 13:23:05'),
(12, 13, 25, 'ARTIST UPDATE: Status changed to Items Prepared.', 'Artist', 'Items Prepared', 0, '2026-04-16 13:23:10'),
(13, 13, 25, 'ARTIST UPDATE: Status changed to Ready for Pickup.', 'Artist', 'Ready for Pickup', 0, '2026-04-16 13:23:16'),
(14, 13, 25, 'ARTIST UPDATE: Status changed to Item Picked Up.', 'Artist', 'Item Picked Up', 0, '2026-04-16 13:23:20');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `ORDER_ID` int(11) NOT NULL,
  `USER_ID` int(11) DEFAULT NULL,
  `PAYMENT_ID` int(11) DEFAULT NULL,
  `SHIPMENT_ID` int(11) DEFAULT NULL,
  `ORDER_TOTAL_QUANTITY` int(11) DEFAULT NULL,
  `ORDER_DELIVERY_FEE` decimal(10,2) DEFAULT NULL,
  `ORDER_TOTAL_AMOUNT` decimal(10,2) DEFAULT NULL,
  `ORDER_STATUS` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`ORDER_ID`, `USER_ID`, `PAYMENT_ID`, `SHIPMENT_ID`, `ORDER_TOTAL_QUANTITY`, `ORDER_DELIVERY_FEE`, `ORDER_TOTAL_AMOUNT`, `ORDER_STATUS`) VALUES
(12, 12, 12, NULL, 1, 60.00, 110.00, 'Shipped'),
(13, 12, 13, NULL, 1, 60.00, 110.00, 'Delivered');

-- --------------------------------------------------------

--
-- Table structure for table `order_details`
--

CREATE TABLE `order_details` (
  `id` int(11) NOT NULL,
  `ORDER_ID` int(11) NOT NULL,
  `PROD_ID` int(11) NOT NULL,
  `PRICE` decimal(10,2) DEFAULT NULL,
  `QUANTITY` int(11) DEFAULT NULL,
  `DISCOUNT` decimal(10,2) DEFAULT NULL,
  `SUBTOTAL` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_details`
--

INSERT INTO `order_details` (`id`, `ORDER_ID`, `PROD_ID`, `PRICE`, `QUANTITY`, `DISCOUNT`, `SUBTOTAL`) VALUES
(12, 12, 5, 50.00, 1, NULL, 50.00),
(13, 13, 5, 50.00, 1, NULL, 50.00);

-- --------------------------------------------------------

--
-- Table structure for table `payment`
--

CREATE TABLE `payment` (
  `PAYMENT_ID` int(11) NOT NULL,
  `PAYMENT_TIMESTAMP` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `PAYMENT_METHOD` varchar(50) DEFAULT NULL,
  `PAYMENT_STATUS` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payment`
--

INSERT INTO `payment` (`PAYMENT_ID`, `PAYMENT_TIMESTAMP`, `PAYMENT_METHOD`, `PAYMENT_STATUS`) VALUES
(12, '2026-04-16 13:21:13', 'Cash on Delivery', 'Pending'),
(13, '2026-04-16 13:22:46', 'Cash on Delivery', 'Pending');

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `PROD_ID` int(11) NOT NULL,
  `ARTIST_ID` int(11) DEFAULT NULL,
  `CATEGORY_ID` int(11) DEFAULT NULL,
  `PROD_NAME` varchar(255) DEFAULT NULL,
  `PROD_DESCRIPTION` text DEFAULT NULL,
  `PROD_PRICE` decimal(10,2) DEFAULT NULL,
  `PROD_STOCK_QTY` int(11) DEFAULT NULL,
  `PROD_IMAGE` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`PROD_ID`, `ARTIST_ID`, `CATEGORY_ID`, `PROD_NAME`, `PROD_DESCRIPTION`, `PROD_PRICE`, `PROD_STOCK_QTY`, `PROD_IMAGE`) VALUES
(5, 25, 3, 'Fish', 'Fishes', 50.00, 48, 'artwork_pics/misteryoso_2.png'),
(6, 26, 3, 'K3 Artwork', 'High-quality digital print', 150.00, 10, 'artwork_pics/K3 2.png'),
(7, 25, 1, 'K4 Artwork', 'Limited edition Bicolano art', 200.00, 5, 'artwork_pics/K4 2.png'),
(8, 27, 8, 'LoseLose', 'Modern abstract concept', 120.00, 15, 'artwork_pics/loselose 2.png'),
(9, 25, 4, 'Lyrics 4Wx3H', 'Typography focused artwork', 85.00, 20, 'artwork_pics/LYRICS 4Wx3H INCHES 2.png'),
(10, 26, 2, 'Matcha', 'Minimalist green aesthetic', 95.00, 12, 'artwork_pics/matcha 2.png'),
(11, 27, 5, 'Meowcean Eyes', 'Surreal ocean-themed illustration', 350.00, 3, 'artwork_pics/meowcean eyes 2.png'),
(12, 25, 6, 'Version B', 'Alternative design variant', 110.00, 8, 'artwork_pics/ver b 2.png'),
(13, 26, 1, 'Yellow Study', 'Vibrant yellow composition', 130.00, 7, 'artwork_pics/yellow 2.png'),
(14, 27, 3, 'A Version', 'Primary concept artwork', 140.00, 9, 'artwork_pics/a ver 2.png'),
(15, 25, 7, 'And If I Cry', 'Emotional expressionist piece', 500.00, 2, 'artwork_pics/and if I cry 2.png'),
(16, 26, 2, 'Dmtry', 'Experimental portraiture', 275.00, 4, 'artwork_pics/dmtry 2.png');

-- --------------------------------------------------------

--
-- Table structure for table `review`
--

CREATE TABLE `review` (
  `REVIEW_ID` int(11) NOT NULL,
  `USER_ID` int(11) DEFAULT NULL,
  `PRODUCT_ID` int(11) DEFAULT NULL,
  `REVIEW_RATING` int(11) DEFAULT NULL,
  `REVIEW_DESCRIPTION` text DEFAULT NULL,
  `REVIEW_IMAGE` varchar(255) DEFAULT NULL,
  `DATE_CREATED` timestamp NOT NULL DEFAULT current_timestamp(),
  `DATE_DELETED` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `shipment`
--

CREATE TABLE `shipment` (
  `SHIPMENT_ID` int(11) NOT NULL,
  `ADDRESS_ID` int(11) DEFAULT NULL,
  `SHIPMENT_DATE` date DEFAULT NULL,
  `SHIPMENT_COMPANY` varchar(100) DEFAULT NULL,
  `SHIPMENT_STATUS` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `supply_inventory`
--

CREATE TABLE `supply_inventory` (
  `SUPPLY_ID` int(11) NOT NULL,
  `PROD_ID` int(11) DEFAULT NULL,
  `SUPPLIED_DATE` date DEFAULT NULL,
  `SUPPLIED_QTY` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `address`
--
ALTER TABLE `address`
  ADD PRIMARY KEY (`ADDRESS_ID`),
  ADD KEY `fk_address_django_user` (`USER_ID`);

--
-- Indexes for table `artist`
--
ALTER TABLE `artist`
  ADD PRIMARY KEY (`ARTIST_ID`),
  ADD KEY `fk_artist_user` (`USER_ID`);

--
-- Indexes for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`CART_ID`),
  ADD KEY `fk_cart_django_user` (`USER_ID`);

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_cart_product` (`CART_ID`,`PRODUCT_ID`),
  ADD KEY `PRODUCT_ID` (`PRODUCT_ID`);

--
-- Indexes for table `category`
--
ALTER TABLE `category`
  ADD PRIMARY KEY (`CATEGORY_ID`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`LIKE_ID`),
  ADD KEY `PRODUCT_ID` (`PRODUCT_ID`),
  ADD KEY `fk_like_django_user` (`USER_ID`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `artist_id` (`artist_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`ORDER_ID`),
  ADD UNIQUE KEY `PAYMENT_ID` (`PAYMENT_ID`),
  ADD UNIQUE KEY `SHIPMENT_ID` (`SHIPMENT_ID`),
  ADD KEY `fk_order_django_user` (`USER_ID`);

--
-- Indexes for table `order_details`
--
ALTER TABLE `order_details`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_order_product` (`ORDER_ID`,`PROD_ID`),
  ADD KEY `order_details_ibfk_2` (`PROD_ID`);

--
-- Indexes for table `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`PAYMENT_ID`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`PROD_ID`),
  ADD KEY `ARTIST_ID` (`ARTIST_ID`),
  ADD KEY `CATEGORY_ID` (`CATEGORY_ID`);

--
-- Indexes for table `review`
--
ALTER TABLE `review`
  ADD PRIMARY KEY (`REVIEW_ID`),
  ADD KEY `PRODUCT_ID` (`PRODUCT_ID`),
  ADD KEY `fk_review_django_user` (`USER_ID`);

--
-- Indexes for table `shipment`
--
ALTER TABLE `shipment`
  ADD PRIMARY KEY (`SHIPMENT_ID`),
  ADD KEY `ADDRESS_ID` (`ADDRESS_ID`);

--
-- Indexes for table `supply_inventory`
--
ALTER TABLE `supply_inventory`
  ADD PRIMARY KEY (`SUPPLY_ID`),
  ADD KEY `PROD_ID` (`PROD_ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `address`
--
ALTER TABLE `address`
  MODIFY `ADDRESS_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `artist`
--
ALTER TABLE `artist`
  MODIFY `ARTIST_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `CART_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `cart_items`
--
ALTER TABLE `cart_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `category`
--
ALTER TABLE `category`
  MODIFY `CATEGORY_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `likes`
--
ALTER TABLE `likes`
  MODIFY `LIKE_ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `ORDER_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `order_details`
--
ALTER TABLE `order_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `payment`
--
ALTER TABLE `payment`
  MODIFY `PAYMENT_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `PROD_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `review`
--
ALTER TABLE `review`
  MODIFY `REVIEW_ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `address`
--
ALTER TABLE `address`
  ADD CONSTRAINT `fk_address_django_user` FOREIGN KEY (`USER_ID`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `artist`
--
ALTER TABLE `artist`
  ADD CONSTRAINT `fk_artist_user` FOREIGN KEY (`USER_ID`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `fk_cart_django_user` FOREIGN KEY (`USER_ID`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`CART_ID`) REFERENCES `cart` (`CART_ID`),
  ADD CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`PRODUCT_ID`) REFERENCES `product` (`PROD_ID`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `likes`
--
ALTER TABLE `likes`
  ADD CONSTRAINT `fk_like_django_user` FOREIGN KEY (`USER_ID`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`PRODUCT_ID`) REFERENCES `product` (`PROD_ID`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`ORDER_ID`),
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`artist_id`) REFERENCES `artist` (`ARTIST_ID`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `fk_order_django_user` FOREIGN KEY (`USER_ID`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`PAYMENT_ID`) REFERENCES `payment` (`PAYMENT_ID`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`SHIPMENT_ID`) REFERENCES `shipment` (`SHIPMENT_ID`);

--
-- Constraints for table `order_details`
--
ALTER TABLE `order_details`
  ADD CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`ORDER_ID`) REFERENCES `orders` (`ORDER_ID`),
  ADD CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`PROD_ID`) REFERENCES `product` (`PROD_ID`) ON DELETE CASCADE;

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`ARTIST_ID`) REFERENCES `artist` (`ARTIST_ID`),
  ADD CONSTRAINT `product_ibfk_2` FOREIGN KEY (`CATEGORY_ID`) REFERENCES `category` (`CATEGORY_ID`);

--
-- Constraints for table `review`
--
ALTER TABLE `review`
  ADD CONSTRAINT `fk_review_django_user` FOREIGN KEY (`USER_ID`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `review_ibfk_2` FOREIGN KEY (`PRODUCT_ID`) REFERENCES `product` (`PROD_ID`) ON DELETE CASCADE;

--
-- Constraints for table `shipment`
--
ALTER TABLE `shipment`
  ADD CONSTRAINT `shipment_ibfk_1` FOREIGN KEY (`ADDRESS_ID`) REFERENCES `address` (`ADDRESS_ID`);

--
-- Constraints for table `supply_inventory`
--
ALTER TABLE `supply_inventory`
  ADD CONSTRAINT `supply_inventory_ibfk_1` FOREIGN KEY (`PROD_ID`) REFERENCES `product` (`PROD_ID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
