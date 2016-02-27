SET autocommit=0;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `version_alluc` (
	`db_version` int(11) NOT NULL DEFAULT 1,
	PRIMARY KEY(`db_version`)
);

CREATE TABLE IF NOT EXISTS `favorites` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`media` VARCHAR(10) NULL DEFAULT 'TV', 
	`name` VARCHAR(125) NULL, 
	`imdb_id` VARCHAR(15) NULL, 
	`new` TINYINT NULL DEFAULT 0, 
	PRIMARY KEY (`id`), 
	UNIQUE INDEX `imdb_id_UNIQUE` (`imdb_id` ASC)
);

CREATE TABLE IF NOT EXISTS `subscriptions` (
	`id` int(11) NOT NULL AUTO_INCREMENT, 
	`imdb_id` VARCHAR(15) NULL, 
	`title` VARCHAR(225) NULL, 
	`enabled` TINYINT(1) DEFAULT 1, 
	PRIMARY KEY (`id`), 
	UNIQUE INDEX `imdb_id_UNIQUE` (`imdb_id` ASC)
);

CREATE TABLE IF NOT EXISTS `lists` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`list` VARCHAR(125) NULL, 
	`slug` VARCHAR(125) NULL, 
	`media` VARCHAR(10) NULL, 
	`sync` TINYINT(1) DEFAULT 1, 
	PRIMARY KEY (`id`), 
	UNIQUE INDEX `slug_UNIQUE` (`slug`, `media` ASC)
);

CREATE TABLE IF NOT EXISTS `list_movies`(
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`list_id` int(11) NOT NULL, 
	`imdb_id` VARCHAR(15) NULL, 
	`path` VARCHAR(255) NULL, 
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `hosts` (
	`id` INT NOT NULL AUTO_INCREMENT, 
	`host` VARCHAR(75) NULL, 
	`title` VARCHAR(75) NULL, 
	`enabled` TINYINT NULL DEFAULT 1, 
	PRIMARY KEY (`id`), 
	UNIQUE INDEX `host_UNIQUE` (`host` ASC)
);

CREATE TABLE IF NOT EXISTS `fetch_count` (
	`id` int(11) NOT NULL AUTO_INCREMENT, 
	`num` int(11) DEFAULT NULL, 
	`ts` date DEFAULT NULL, 
	PRIMARY KEY (`id`), 
	UNIQUE KEY `ts_UNIQUE` (`ts`)
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

COMMIT;

SET autocommit=1;


