CREATE TABLE IF NOT EXISTS "version" (
	"db_version" INTEGER DEFAULT 1 UNIQUE,
	PRIMARY KEY(db_version)
);

DROP TABLE "search_cache";

DROP VIEW "fresh_cache";

CREATE TABLE IF NOT EXISTS "search_cache" (
	"cache_id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"hash" TEXT NOT NULL,
	"service" TEXT NOT NULL,
	"host" TEXT NOT NULL,
	"display" TEXT NOT NULL,
	"quality" INTEGER DEFAULT 3,
	"debrid" INTEGER DEFAULT 0,
	"alldebrid" INTEGER DEFAULT 0,
	"realdebrid" INTEGER DEFAULT 0,
	"rpnet" INTEGER DEFAULT 0,
	"premiumize" INTEGER DEFAULT 0,
	"url" TEXT NOT NULL, 
	"ts" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "scraper_states" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"name" TEXT UNIQUE,
	"enabled" INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS "scraper_stats" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"service" TEXT,
	"host" TEXT,
	"attempts" FLOAT DEFAULT (0),
	"resolved" FLOAT DEFAULT (0),
	"success" FLOAT DEFAULT (0),
	UNIQUE ("service", "host") ON CONFLICT REPLACE
);

CREATE TABLE IF NOT EXISTS "playback_states" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"imdb_id" TEXT,
	"season" INTEGER,
	"episode" INTEGER,
	"current" TEXT,
	"total" TEXT,
	UNIQUE ("imdb_id", "season", episode) ON CONFLICT REPLACE
);

CREATE TABLE IF NOT EXISTS "host_weights" (
	"id" INTEGER PRIMARY KEY NOT NULL,
	"host" TEXT,
	"weight" INTEGER DEFAULT (1000),
	"disabled" INTEGER DEFAULT (0),
	UNIQUE ("host") ON CONFLICT IGNORE
);

CREATE TABLE IF NOT EXISTS "tvshow_favorites" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"imdb_id" TEXT,
	"tmdb_id" TEXT,
	"tvdb_id" TEXT,
	"trakt_id" TEXT,
	"slug" TEXT,
	"title" TEXT,
	"TVShowTitle" TEXT,
	"rating" FLOAT,
	"duration" TEXT,
	"plot" TEXT,
	"mpaa" TEXT,
	"premiered" TEXT,
	"year" INTEGER,
	"trailer_url" TEXT,
	"genre" TEXT,
	"studio" TEXT,
	"status" TEXT,
	"cast" TEXT,
	"banner_url" TEXT,
	"cover_url" TEXT,
	"backdrop_url" TEXT,
	UNIQUE (imdb_id, tmdb_id, title)
);

CREATE TABLE IF NOT EXISTS "movie_favorites"(
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"imdb_id" TEXT,
	"tmdb_id" TEXT,
	"trakt_id" TEXT,
	"slug" TEXT,
	"title" TEXT,
	"writer" TEXT,
	"director" TEXT,
	"rating" FLOAT,
	"votes" TEXT,
	"duration" TEXT,
	"plot" TEXT,
	"tagline" TEXT,
	"mpaa" TEXT,
	"premiered" TEXT,
	"year" INTEGER,
	"trailer_url" TEXT,
	"genre" TEXT,
	"studio" TEXT,
	"status" TEXT,
	"cast" TEXT,
	"thumb_url" TEXT,
	"cover_url" TEXT,
	"backdrop_url" TEXT,
	UNIQUE (imdb_id, tmdb_id, title)
);

CREATE VIEW IF NOT EXISTS "fresh_cache" AS
	SELECT cache_id, 
	hash as hashid, 
	service, 
	host, 
	display as title, 
	url, 
	quality,
	debrid,
	alldebrid,
	realdebrid,
	rpnet,
	premiumize, 
	strftime("%s",'now') -  strftime("%s",ts) < (3600 * 2) AS fresh 
	FROM search_cache  
	WHERE fresh = 1
;

CREATE VIEW IF NOT EXISTS "stale_cache" AS
	SELECT cache_id, 
	hash, 
	strftime("%s",'now') -  strftime("%s",ts) > (3600 * 2) AS stale 
	FROM search_cache 
	WHERE stale = 1
;

CREATE VIEW IF NOT EXISTS "host_ranks" AS
	SELECT host, 
	((1000 - weight) - (10000 * disabled)) as rank, 
	weight 
	FROM host_weights 
	WHERE rank >= 0 
	ORDER BY weight, host ASC
;