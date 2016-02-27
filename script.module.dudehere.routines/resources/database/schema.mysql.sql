SET autocommit=0;

START TRANSACTION;

DROP TABLE `search_cache`;

DROP VIEW `fresh_cache`';

CREATE TABLE IF NOT EXISTS `version` (
	`db_version` int(11) NOT NULL DEFAULT 1,
	PRIMARY KEY(`db_version`)
);

CREATE TABLE IF NOT EXISTS `scraper_states` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(150) NOT NULL,
	`enabled` int(11) NOT NULL DEFAULT '1',
	PRIMARY KEY (`id`),
	UNIQUE KEY `name_UNIQUE` (`name`)
);

CREATE TABLE IF NOT EXISTS `scraper_stats` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`service` varchar(150) DEFAULT NULL,
	`host` varchar(150) DEFAULT NULL,
	`attempts` FLOAT NOT NULL DEFAULT '0',
	`resolved` FLOAT NOT NULL DEFAULT '0',
	`success` FLOAT NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE KEY `service_UNIQUE` (`service`,`host`)
);

CREATE TABLE IF NOT EXISTS `search_cache` (
	`cache_id` int(11) NOT NULL AUTO_INCREMENT,
	`hash` varchar(255) NOT NULL,
	`service` varchar(45) NOT NULL,
	`host` varchar(45) NOT NULL,
	`display` varchar(255) NOT NULL,
	`quality` int(11) DEFAULT '3',
	`debrid` int(11) DEFAULT '0',
	`alldebrid` int(11) DEFAULT '0',
	`realdebrid` int(11) DEFAULT '0',
	`rpnet` int(11) DEFAULT '0',
	`premiumize` int(11) DEFAULT '0',
	`url` varchar(255) NOT NULL,
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`cache_id`)
);

CREATE TABLE IF NOT EXISTS `playback_states` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`imdb_id` varchar(45) DEFAULT NULL,
	`season` int(11) DEFAULT '0',
	`episode` int(11) DEFAULT '0',
	`current` varchar(45) DEFAULT NULL,
	`total` varchar(45) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `imdb_id_UNIQUE` (`imdb_id`,`season`,`episode`)
);

CREATE TABLE IF NOT EXISTS `host_weights` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`host` varchar(150) DEFAULT NULL,
	`weight` int(11) DEFAULT '1000',
	`disabled` tinyint(1) DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE KEY `host_UNIQUE` (`host`)
);

CREATE TABLE IF NOT EXISTS `tvshow_favorites` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`imdb_id` varchar(45) DEFAULT NULL,
	`tmdb_id` varchar(45) DEFAULT NULL,
	`tvdb_id` varchar(45) DEFAULT NULL,
	`trakt_id` varchar(45) DEFAULT NULL,
	`slug` varchar(150) DEFAULT NULL,
	`title` varchar(255) DEFAULT NULL,
	`TVShowTitle` varchar(255) DEFAULT NULL,
	`rating` FLOAT(10,8),
	`duration` varchar(45) DEFAULT NULL,
	`plot` varchar(255) DEFAULT NULL,
	`mpaa` varchar(45) DEFAULT NULL,
	`premiered` varchar(45) DEFAULT NULL,	
	`year` int(4),
	`trailer_url` varchar(255) DEFAULT NULL,
	`genre` varchar(150) DEFAULT NULL,
	`studo` varchar(45) DEFAULT NULL,
	`status` varchar(45) DEFAULT NULL,
	`cast` varchar(45) DEFAULT NULL,
	`banner_url` varchar(255) DEFAULT NULL,
	`cover_url` varchar(255) DEFAULT NULL,
	`backdrop_url` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `movie_UNIQUE` (`imdb_id`, `tmdb_id`, `title`)
);

CREATE TABLE IF NOT EXISTS `movie_favorites`(
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`imdb_id` varchar(45) DEFAULT NULL,
	`tmdb_id` varchar(45) DEFAULT NULL,
	`trakt_id` varchar(45) DEFAULT NULL,
	`slug` varchar(150) DEFAULT NULL,
	`title` varchar(255) DEFAULT NULL,
	`writer` varchar(45) DEFAULT NULL,
	`director` varchar(45) DEFAULT NULL,
	`rating` varchar(15) DEFAULT NULL,
	`votes` varchar(15) DEFAULT NULL,
	`duration` varchar(45) DEFAULT NULL,
	`plot` varchar(255) DEFAULT NULL,
	`mpaa` varchar(45) DEFAULT NULL,
	`tagline` varchar(255) DEFAULT NULL,
	`premiered` varchar(45) DEFAULT NULL,	
	`year` int(4),
	`trailer_url` varchar(255) DEFAULT NULL,
	`genre` varchar(150) DEFAULT NULL,
	`studo` varchar(45) DEFAULT NULL,
	`status` varchar(45) DEFAULT NULL,
	`cast` varchar(45) DEFAULT NULL,
	`thumb_url` varchar(255) DEFAULT NULL,
	`cover_url` varchar(255) DEFAULT NULL,
	`backdrop_url` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `movie_UNIQUE` (`imdb_id`, `tmdb_id`, `title`)
);

CREATE OR REPLACE VIEW `fresh_cache` AS
	SELECT 
		`search_cache`.`cache_id` AS `cache_id`,
		`search_cache`.`hash` AS `hashid`,
		`search_cache`.`service` AS `service`,
		`search_cache`.`host` AS `host`,
		`search_cache`.`display` AS `title`,
		`search_cache`.`url` AS `url`,
		`search_cache`.`quality` AS `quality`,
		`search_cache`.`debrid` AS `debrid`,
		`search_cache`.`alldebrid` AS `alldebrid`,
		`search_cache`.`realdebrid` AS `realdebrid`,
		`search_cache`.`rpnet` AS `rpnet`,
		`search_cache`.`premiumize` AS `premiumize`,
		(timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) > 120) AS `fresh`
	FROM `search_cache`
	WHERE (timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) > 120)
;

CREATE OR REPLACE VIEW `stale_cache` AS
	SELECT 
		`search_cache`.`cache_id` AS `cache_id`,
		`search_cache`.`hash` AS `hashid`,
		(timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) < 120) AS `stale`
	FROM `search_cache`
	WHERE (timestampdiff(MINUTE, `search_cache`.`ts`, NOW()) < 120)
;

CREATE OR REPLACE VIEW `host_ranks` AS
	SELECT host, 
	((1000 - weight) - (10000 * disabled)) as rank, 
	weight 
	FROM host_weights 
	WHERE ((1000 - weight) - (10000 * disabled)) >= 0 
	ORDER BY weight, host ASC
;

COMMIT;

SET autocommit=1;
