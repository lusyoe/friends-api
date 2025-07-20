CREATE DATABASE IF NOT EXISTS `blog` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `blog`;

CREATE TABLE IF NOT EXISTS `friend_links`(
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rss_url` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT '1',
  `fetch_failed_count` int DEFAULT '0',
  `last_fetch_status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_fetched_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `friend_rss_articles`(
  `id` int NOT NULL AUTO_INCREMENT,
  `friend_id` bigint NOT NULL,
  `title` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `link` varchar(1024) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=982 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS `friend_rss_fetch_logs`(
  `id` int NOT NULL AUTO_INCREMENT,
  `friend_id` bigint NOT NULL,
  `rss_url` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `http_status` int DEFAULT NULL,
  `message` text,
  `fetched_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=366 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;