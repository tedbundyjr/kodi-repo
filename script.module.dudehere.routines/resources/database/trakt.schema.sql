CREATE TABLE IF NOT EXISTS "version" (
	"db_version" INTEGER DEFAULT 1 UNIQUE,
	PRIMARY KEY(db_version)
);

CREATE TABLE IF NOT EXISTS "cache" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"hash_id" TEXT UNIQUE,
	"media" TEXT,
	"url" TEXT,
	"results" TEXT,
	"ts" TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS "id_cache" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"title" TEXT,
	"year" INTEGER,
	"media" TEXT,
	"imdb_id" TEXT UNIQUE,
	"tmdb_id" TEXT,
	"trakt_id" INTEGER
);

CREATE TABLE IF NOT EXISTS "tvshows" (
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
	"overlay" INTEGER,
	"playcount" INTEGER,
	UNIQUE (imdb_id, tmdb_id, title)
);

CREATE TABLE IF NOT EXISTS "episodes"(
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"imdb_id" TEXT,
	"tmdb_id" TEXT,
	"tvdb_id" TEXT,
	"trakt_id" TEXT,
	"slug" TEXT,
	"title" TEXT,
	"showtitle" TEXT,
	"season" INTEGER,
	"episode" INTEGER,
	"episode_id" TEXT,
	"year" INTEGER,
	"duration" TEXT,
	"director" TEXT,
	"writer" TEXT,
	"plot" TEXT,
	"rating" FLOAT,
	"premiered" TEXT,
	"poster" TEXT,
	"cover_url" TEXT,
	"backdrop_url" TEXT,
	"overlay" INTEGER,
	"playcount" INTEGER,
	UNIQUE (imdb_id, tmdb_id, season, episode)
);

CREATE TABLE IF NOT EXISTS "movies"(
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
	"overlay" INTEGER,
	"playcount" INTEGER,
	UNIQUE (imdb_id, tmdb_id, title)
);

CREATE VIEW IF NOT EXISTS "stale_cache" AS
	SELECT id, 
	hash_id, 
	strftime("%s",'now') -  strftime("%s",ts) > (3600 * 2) AS stale 
	FROM cache 
	WHERE stale = 1
;
