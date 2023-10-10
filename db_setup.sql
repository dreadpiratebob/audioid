DROP DATABASE audioid;
DROP USER 'audioid_user'@'localhost';
DROP USER 'audioid_admin'@'localhost';

CREATE DATABASE audioid CHARACTER SET UTF8mb4 COLLATE utf8mb4_bin;
USE audioid;

# change the passwords here.
CREATE USER 'audioid_user'@'localhost' IDENTIFIED BY 'squiggly music';
CREATE USER 'audioid_admin'@'localhost' IDENTIFIED BY 'hey look - a password';

CREATE TABLE catalogs
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(64) not null COLLATE utf8mb4_bin,
  base_path varchar(1024) COLLATE utf8mb4_bin,
  unique(name),
  unique(base_path)
);

GRANT SELECT ON audioid.catalogs TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.catalogs TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.catalogs TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.catalogs TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.catalogs TO 'audioid_admin'@'localhost';

CREATE TABLE songs
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  year int(16) unsigned,
  duration real(15, 10) unsigned,
  filename varchar(1024) not null COLLATE utf8mb4_bin,
  catalog_id int(64) unsigned not null,
  last_scanned int(64) unsigned not null default 0,
  mp3_exists int(1) unsigned not null default 1,
  UNIQUE(id),
  FOREIGN KEY (catalog_id)
    REFERENCES catalogs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.songs TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.songs TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.songs TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.songs TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.songs TO 'audioid_admin'@'localhost';

CREATE TABLE artists
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  UNIQUE(id)
);

GRANT SELECT ON audioid.artists TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.artists TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.artists TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.artists TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.artists TO 'audioid_admin'@'localhost';

CREATE TABLE songs_artists
(
  song_id int(64) unsigned not null,
  artist_id int(64) unsigned not null,
  list_order int(4) unsigned not null,
  conjunction varchar(64) not null default "" COLLATE utf8mb4_bin,
  CONSTRAINT s_ar_pkey PRIMARY KEY (song_id, artist_id),
  UNIQUE(song_id, artist_id),
  FOREIGN KEY (song_id)
    REFERENCES songs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (artist_id)
    REFERENCES artists(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.songs_artists TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.songs_artists TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.songs_artists TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.songs_artists TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.songs_artists TO 'audioid_admin'@'localhost';

CREATE TABLE albums
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  album_artist int(64) unsigned,
  UNIQUE(id),
  FOREIGN KEY (album_artist)
    REFERENCES artists(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.albums TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.albums TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.albums TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.albums TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.albums TO 'audioid_admin'@'localhost';

CREATE TABLE songs_albums
(
  song_id int(64) unsigned not null,
  album_id int(64) unsigned not null,
  track_number int(64) unsigned default null,
  CONSTRAINT s_al_pkey PRIMARY KEY (song_id, album_id),
  UNIQUE(song_id, album_id),
  FOREIGN KEY (song_id)
    REFERENCES songs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (album_id)
    REFERENCES albums(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.songs_albums TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.songs_albums TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.songs_albums TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.songs_albums TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.songs_albums TO 'audioid_admin'@'localhost';

CREATE TABLE genres
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  UNIQUE(id)
);

GRANT SELECT ON audioid.genres TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.genres TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.genres TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.genres TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.genres TO 'audioid_admin'@'localhost';

CREATE TABLE songs_genres
(
  song_id int(64) unsigned not null,
  genre_id int(64) unsigned not null,
  CONSTRAINT s_g_pkey PRIMARY KEY (song_id, genre_id),
  UNIQUE (song_id, genre_id),
  FOREIGN KEY (song_id)
    REFERENCES songs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (genre_id)
    REFERENCES genres(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.songs_genres TO 'audioid_user'@'localhost';
GRANT INSERT ON audioid.songs_genres TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.songs_genres TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.songs_genres TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.songs_genres TO 'audioid_admin'@'localhost';

CREATE TABLE log_levels
(
  id INT(2) unsigned not null primary key,
  log_level VARCHAR(7) not null
);

INSERT INTO log_levels
      (id, log_level)
VALUES (0, "debug"),
       (1, "info"),
       (2, "warning"),
       (3, "error");

GRANT SELECT ON audioid.log_levels TO 'audioid_admin'@'localhost';

CREATE TABLE logging
(
  message TEXT not null,
  log_level INT(2) unsigned not null,
  log_time INT(64) unsigned not null,
  FOREIGN KEY (log_level)
    REFERENCES log_levels(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.logging TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE log_message(IN in_message TEXT, IN in_log_level INT(2) unsigned)
log_message:BEGIN
  INSERT INTO logging (message, log_level, log_time) VALUES(in_message, in_log_level, unix_timestamp());
END//

CREATE PROCEDURE log_debug(IN in_message TEXT)
log_debug:BEGIN
  CALL log_message(in_message, 0);
END//
GRANT EXECUTE ON PROCEDURE audioid.log_debug TO 'audioid_user'@'localhost'//
GRANT EXECUTE ON PROCEDURE audioid.log_debug TO 'audioid_admin'@'localhost'//

CREATE PROCEDURE log_info(IN in_message TEXT)
log_info:BEGIN
  CALL log_message(in_message, 1);
END//
GRANT EXECUTE ON PROCEDURE audioid.log_info TO 'audioid_user'@'localhost'//
GRANT EXECUTE ON PROCEDURE audioid.log_info TO 'audioid_admin'@'localhost'//

CREATE PROCEDURE log_warning(IN in_message TEXT)
log_warning:BEGIN
  CALL log_message(in_message, 2);
END//
GRANT EXECUTE ON PROCEDURE audioid.log_warning TO 'audioid_user'@'localhost'//
GRANT EXECUTE ON PROCEDURE audioid.log_warning TO 'audioid_admin'@'localhost'//

CREATE PROCEDURE log_error(IN in_message TEXT)
log_error:BEGIN
  CALL log_message(in_message, 3);
END//
GRANT EXECUTE ON PROCEDURE audioid.log_error TO 'audioid_user'@'localhost'//
GRANT EXECUTE ON PROCEDURE audioid.log_error TO 'audioid_admin'@'localhost'//

DELIMITER ;

CREATE TABLE song_similarity
(
  song1 int(64) unsigned not null,
  song2 int(64) unsigned not null,
  similarity int(8) unsigned not null,
  FOREIGN KEY (song1)
    REFERENCES songs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (song2)
    REFERENCES songs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE upsert_song_artist_info
(
  artist_name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  list_order int(4) unsigned not null,
  conjunction varchar(64) not null default "" COLLATE utf8mb4_bin
);

GRANT INSERT ON audioid.upsert_song_artist_info TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.upsert_song_artist_info TO 'audioid_admin'@'localhost';
GRANT UPDATE ON audioid.upsert_song_artist_info TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.upsert_song_artist_info TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE FUNCTION begin_scan_get_last_updated(in_catalog_id INT(64) unsigned, in_filename VARCHAR(1024))
RETURNS INT(64) unsigned
BEGIN
  DECLARE var_last_scanned INT(64) unsigned DEFAULT NULL;

  UPDATE songs SET mp3_exists = 1 WHERE catalog_id = in_catalog_id AND filename = in_filename;

  SELECT last_scanned INTO var_last_scanned FROM songs WHERE catalog_id = in_catalog_id AND filename = in_filename;
  RETURN var_last_scanned;
END//

GRANT EXECUTE ON FUNCTION audioid.begin_scan_get_last_updated TO 'audioid_admin'@'localhost'//

CREATE PROCEDURE upsert_song(IN in_song_name VARCHAR(128), IN in_filename VARCHAR(1024), IN in_year INT(16) unsigned, IN in_duration REAL(15, 10) unsigned,
                             IN in_catalog_id INT(64) unsigned, IN in_genre_name VARCHAR(64), IN in_album_name VARCHAR(128),
                             IN in_album_artist_name VARCHAR(128), IN in_track_number INT(64) unsigned, in_last_modified INT(64) unsigned)
upsert_song:BEGIN
  DECLARE var_song_id      INT(64) unsigned DEFAULT NULL;
  DECLARE var_genre_id     INT(64) unsigned DEFAULT NULL;
  DECLARE var_album_id     INT(64) unsigned DEFAULT NULL;
  DECLARE var_last_scanned INT(64) unsigned default NULL;
  DECLARE var_rollback     BOOL DEFAULT 0;
  DECLARE var_artist_id    INT(64) unsigned DEFAULT NULL;
  DECLARE var_artist_name  VARCHAR(1024) DEFAULT "";
  DECLARE var_list_order   INT(4) unsigned;
  DECLARE var_conjunction  VARCHAR(64) DEFAULT "";
  DECLARE cursor_done      INT(1) DEFAULT 0;
  DECLARE artist_join_cursor CURSOR FOR SELECT artist_name, conjunction, list_order FROM upsert_song_artist_info ORDER BY list_order;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET cursor_done = 1;

  -- DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;

  -- START TRANSACTION;

  SELECT id, last_scanned INTO var_song_id, var_last_scanned FROM songs WHERE filename = in_filename AND catalog_id = in_catalog_id;
  
  -- CALL log_debug("existing id:");
  -- CALL log_debug(var_song_id);
  
  IF var_song_id IS NULL THEN
    -- CALL log_debug(CONCAT("inserting ", in_song_name, "..."));
    INSERT INTO songs (name, filename, `year`, duration, catalog_id, last_scanned)
      VALUES(in_song_name, in_filename, in_year, in_duration, in_catalog_id, unix_timestamp());
    SELECT LAST_INSERT_ID() INTO var_song_id;
  ELSE
    IF var_last_scanned > in_last_modified THEN
      -- CALL log_debug(CONCAT("song id ", var_song_id, " was last scanned after it was last modified.",
      --  " (last_scanned=", var_last_scanned, "; last_modified=", in_last_modified, ")"));
      LEAVE upsert_song;
    END IF;
    
    -- CALL log_debug(CONCAT("updating ", in_song_name, "..."));
    UPDATE songs SET name=in_song_name, year=in_year, duration=in_duration, last_scanned=unix_timestamp(), mp3_exists=1 WHERE id=var_song_id;
  END IF;

  -- CALL log_debug(CONCAT("this song's new id is ", var_song_id));

  DELETE FROM songs_genres WHERE song_id = var_song_id;
  IF in_genre_name IS NOT NULL THEN
    SELECT get_genre_id(in_catalog_id, in_genre_name) INTO var_genre_id;
    INSERT INTO songs_genres (song_id, genre_id) VALUES(var_song_id, var_genre_id);
  END IF;

  DELETE FROM songs_artists WHERE song_id = var_song_id;
  SET cursor_done = 0;
  OPEN artist_join_cursor;
  artist_join_loop:LOOP
    FETCH artist_join_cursor INTO var_artist_name, var_conjunction, var_list_order;
    IF cursor_done = 1 THEN
      LEAVE artist_join_loop;
    END IF;

    SELECT get_artist_id(in_catalog_id, var_artist_name) INTO var_artist_id;
    -- not sure if it's faster to do this or set the artist_id in upsert_song_artist_info and do a bulk update.
    INSERT INTO songs_artists (song_id, artist_id, conjunction, list_order)
      VALUES (var_song_id, var_artist_id, var_conjunction, var_list_order);
  END LOOP artist_join_loop;
  CLOSE artist_join_cursor;
  DELETE FROM upsert_song_artist_info WHERE artist_name IS NULL OR artist_name IS NOT NULL;

  DELETE FROM songs_albums WHERE song_id = var_song_id;
  IF in_album_name IS NOT NULL THEN
    SELECT get_album_id(in_catalog_id, in_album_name, in_album_artist_name) INTO var_album_id;
    INSERT INTO songs_albums (song_id, album_id, track_number) VALUES(var_song_id, var_album_id, in_track_number);
  END IF;
  INSERT INTO song_similarity (song1, song2, similarity) VALUES(var_song_id, var_song_id, 255);

  -- IF var_rollback = 1 THEN
  --   ROLLBACK;
  -- ELSE
  --   COMMIT;
  -- END IF;
END//

GRANT EXECUTE ON PROCEDURE audioid.upsert_song TO 'audioid_admin'@'localhost'//

CREATE FUNCTION get_genre_id(in_catalog_id INT(64) unsigned, in_genre_name VARCHAR(64))
RETURNS INT(64) unsigned
BEGIN
  DECLARE var_genre_id INT(64) unsigned DEFAULT NULL;
  
  SELECT g.id INTO var_genre_id
  FROM genres as g
    INNER JOIN songs_genres AS s_g ON s_g.genre_id = g.id
    INNER JOIN songs AS s ON s.id = s_g.song_id
      AND s.catalog_id = in_catalog_id
  WHERE g.name = in_genre_name
  GROUP BY g.id;
  
  IF var_genre_id IS NOT NULL THEN
    RETURN var_genre_id;
  END IF;
  
  INSERT INTO genres (name) VALUES(in_genre_name);
  
  SELECT LAST_INSERT_ID() INTO var_genre_id;
  
  RETURN var_genre_id;
END//

CREATE FUNCTION get_album_id(in_catalog_id INT(64) unsigned, in_album_name VARCHAR(128), in_album_artist_name VARCHAR(128))
RETURNS INT(64) unsigned
BEGIN
  DECLARE var_album_id  INT(64) unsigned DEFAULT NULL;
  DECLARE var_artist_id INT(64) unsigned DEFAULT NULL;
  
  IF in_album_artist_name IS NULL THEN
    SELECT a.id INTO var_album_id
    FROM albums AS a
      INNER JOIN songs_albums AS s_a ON s_a.album_id = a.id
      INNER JOIN songs AS s ON s.id = s_a.song_id
        AND s.catalog_id = in_catalog_id
    WHERE a.name = in_album_name AND album_artist IS NULL
    GROUP BY a.id;
  ELSE
    SELECT get_artist_id(in_catalog_id, in_album_artist_name) INTO var_artist_id;
    SELECT a.id INTO var_album_id
    FROM albums AS a
      INNER JOIN songs_albums AS s_a ON s_a.album_id = a.id
      INNER JOIN songs AS s ON s.id = s_a.song_id
        AND s.catalog_id = in_catalog_id
    WHERE a.name = in_album_name AND album_artist = var_artist_id
    GROUP BY a.id;
  END IF;
  
  IF var_album_id IS NOT NULL THEN
    RETURN var_album_id;
  END IF;
  
  IF in_album_artist_name IS NOT NULL AND var_artist_id IS NULL THEN
    INSERT INTO artists (name) VALUES(in_album_artist_name);
    SELECT LAST_INSERT_ID() INTO var_artist_id;
  END IF;
  
  INSERT INTO albums (name, album_artist) VALUES(in_album_name, var_artist_id);
  SELECT LAST_INSERT_ID() INTO var_album_id;
  
  RETURN var_album_id;
END//

CREATE FUNCTION get_artist_id(in_catalog_id INT(64) unsigned, in_artist_name VARCHAR(128))
RETURNS INT(64) unsigned
BEGIN
  DECLARE var_artist_id INT(64) unsigned DEFAULT NULL;
  DECLARE var_message   VARCHAR(1024) DEFAULT "";

  SELECT a.id INTO var_artist_id
  FROM artists AS a
    INNER JOIN songs_artists AS s_a ON s_a.artist_id = a.id
      INNER JOIN songs AS s ON s.id = s_a.song_id
        AND s.catalog_id = in_catalog_id
  WHERE a.name = in_artist_name
  GROUP BY a.id;

  IF var_artist_id IS NULL THEN
    INSERT INTO artists (name) VALUES(in_artist_name);
    SELECT LAST_INSERT_ID() INTO var_artist_id;
  END IF;

  RETURN var_artist_id;
END//

CREATE PROCEDURE delete_catalog(IN in_catalog_id INT(64) UNSIGNED)
BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  START TRANSACTION;
  
  DELETE FROM songs_artists
  WHERE song_id IN
  (
    SELECT id
    FROM songs
    WHERE songs.catalog_id = in_catalog_id
  );
  
  DELETE FROM artists WHERE id NOT IN
  (
    SELECT DISTINCT artist_id
    FROM songs_artists
  );
  
  DELETE FROM songs_albums
  WHERE song_id IN
  (
    SELECT id
    FROM songs
    WHERE songs.catalog_id = in_catalog_id
  );
  
  DELETE FROM albums WHERE id NOT IN
  (
    SELECT DISTINCT album_id
    FROM songs_albums
  );
  
  DELETE FROM songs_genres
  WHERE song_id IN
  (
    SELECT id
    FROM songs
    WHERE songs.catalog_id = in_catalog_id
  );
  
  DELETE FROM genres
  WHERE id NOT IN
  (
    SELECT DISTINCT genre_id
    FROM songs_genres
  );
  
  DELETE FROM song_similarity
  WHERE song1 IN
  (
    SELECT id
    FROM songs
    WHERE catalog_id = in_catalog_id
  )
  OR
  song2 IN
  (
    SELECT id
    FROM songs
    WHERE catalog_id = in_catalog_id
  );
  
  DELETE FROM songs WHERE catalog_id = in_catalog_id;
  
  DELETE FROM catalogs WHERE id = in_catalog_id;
  
  IF var_rollback THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.delete_catalog TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE delete_songs_without_mp3s(IN in_catalog_id INT(64) unsigned)
delete_songs_without_mp3s:BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  START TRANSACTION;
  
  DELETE FROM songs_albums    WHERE song_id IN (SELECT id FROM songs WHERE catalog_id = in_catalog_id AND mp3_exists = 0);
  DELETE FROM songs_artists   WHERE song_id IN (SELECT id FROM songs WHERE catalog_id = in_catalog_id AND mp3_exists = 0);
  DELETE FROM songs_genres    WHERE song_id IN (SELECT id FROM songs WHERE catalog_id = in_catalog_id AND mp3_exists = 0);
  DELETE FROM song_similarity WHERE song1 IN (SELECT id FROM songs WHERE catalog_id = in_catalog_id AND mp3_exists = 0) OR song2 IN (SELECT id FROM songs WHERE catalog_id = in_catalog_id AND mp3_exists = 0);
  DELETE FROM songs           WHERE catalog_id = in_catalog_id AND mp3_exists = 0;
  
  IF var_rollback THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.delete_songs_without_mp3s TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE delete_song(IN in_song_id INT(64) unsigned)
delete_song:BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;

  START TRANSACTION;

  DELETE FROM songs_albums    WHERE song_id = in_song_id;
  DELETE FROM songs_artists   WHERE song_id = in_song_id;
  DELETE FROM songs_genres    WHERE song_id = in_song_id;
  DELETE FROM song_similarity WHERE song1 = in_song_id OR song2 = in_song_id;
  DELETE FROM songs           WHERE id      = in_song_id;

  IF var_rollback THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.delete_song TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE clean_unused_data()
clean_unused_data:BEGIN
  # i'm not wrapping this in a transaction because it's fine if one these queries fails but the others succeed.
  
  DELETE FROM albums
  WHERE id IN
  (
    SELECT a.id
    FROM albums AS a
      LEFT JOIN songs_albums AS s_a ON s_a.album_id = a.id
    GROUP BY a.id
    HAVING COUNT(s_a.song_id) = 0
  );
  
  DELETE FROM artists
  WHERE id IN
  (
    SELECT a.id
    FROM artists AS a
      LEFT JOIN songs_artists AS s_a ON s_a.artist_id = a.id
    GROUP BY a.id
    HAVING COUNT(s_a.song_id) = 0
  );
  
  DELETE FROM genres
  WHERE id IN
  (
    SELECT g.id
    FROM genres AS g
      LEFT JOIN songs_genres AS s_g ON s_g.genre_id  = g.id
    GROUP BY g.id
    HAVING COUNT(s_g.song_id) = 0
  );
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.clean_unused_data TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE upsert_song_similarity(IN in_song1 INT(64) UNSIGNED, IN in_song2 INT(64) UNSIGNED, IN in_similarity INT(8) UNSIGNED)
upsert_song_similarity:BEGIN
  DECLARE var_id INT(64) UNSIGNED;
  
  SELECT id INTO var_id FROM songs WHERE id = in_song1;
  
  IF var_id IS NULL THEN
    LEAVE upsert_song_similarity;
  END IF;
  
  SELECT id INTO var_id FROM songs WHERE id = in_song2;
  
  IF var_id IS NULL THEN
    LEAVE upsert_song_similarity;
  END IF;
  
  SELECT song1 INTO var_id FROM song_similarity WHERE song1 = in_song1 AND song2 = in_song2;
  
  IF var_id IS NOT NULL THEN
    UPDATE song_similarity SET similarity = in_similarity WHERE (song1 = in_song1 AND song2 = in_song2) OR (song1 = in_song2 AND song2 = in_song1);
    LEAVE upsert_song_similarity;
  END IF;
  
  INSERT INTO song_similarity
  (song1,    song2,    similarity)
  VALUES (in_song1, in_song2, in_similarity);
  
  INSERT INTO song_similarity
  (song1,    song2,    similarity)
  VALUES (in_song2, in_song1, in_similarity);
  
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.upsert_song_similarity TO 'audioid_user'@'localhost';