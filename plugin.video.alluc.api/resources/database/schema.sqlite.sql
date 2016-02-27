CREATE TABLE IF NOT EXISTS "version_alluc" (
	"db_version" INTEGER DEFAULT 1 UNIQUE,
	PRIMARY KEY(db_version)
);

CREATE TABLE IF NOT EXISTS "favorites" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"media" TEXT default "TV", 
	"name" TEXT, 
	"imdb_id" TEXT UNIQUE, 
	"new" INTEGER default 0
);

CREATE TABLE IF NOT EXISTS "subscriptions" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"imdb_id" TEXT UNIQUE, 
	"title" TEXT, 
	"enabled" INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS  "lists" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"list" TEXT, 
	"slug" TEXT, 
	"media" TEXT, 
	"sync" INTEGER DEFAULT (1), 
	UNIQUE (slug, media) ON CONFLICT IGNORE
);

CREATE TABLE IF NOT EXISTS "list_movies" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"list_id" INTEGER, 
	"imdb_id" TEXT, 
	"path" TEXT
);

CREATE TABLE IF NOT EXISTS "hosts" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"host" TEXT UNIQUE, 
	"title" TEXT, 
	"enabled" INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS "fetch_count" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT, 
	"num" INTEGER, 
	"ts" DATE DEFAULT CURRENT_DATE, 
	UNIQUE (ts)  ON CONFLICT REPLACE
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
