CREATE DATABASE audioid;

USE audioid;

# change the passwords here.
CREATE USER 'audioid_user'@'localhost' IDENTIFIED BY 'some password';
CREATE USER 'audioid_admin'@'localhost' IDENTIFIED BY 'other password';

CREATE TABLE catalogs
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(64) not null,
  base_path varchar(1024)
);

GRANT SELECT ON audioid.catalogs TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.catalogs TO 'audioid_user'@'localhost';

CREATE TABLE songs
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(128) not null default "",
  year int(16) unsigned,
  filename varchar(1024) not null,
  catalog_id int(64) unsigned not null,
  FOREIGN KEY (catalog_id)
    REFERENCES catalogs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.songs TO 'audioid_user'@'localhost';
GRANT SELECT ON audioid.songs TO 'audioid_admin'@'localhost';

CREATE TABLE artists
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(128) not null default ""
);

GRANT SELECT ON audioid.artists TO 'audioid_user'@'localhost';

CREATE TABLE songs_artists
(
  song_id int(64) unsigned not null,
  artist_id int(64) unsigned not null,
  list_order int(4) unsigned not null,
  conjunction varchar(24) not null default ", ",
  CONSTRAINT s_ar_pkey PRIMARY KEY (song_id, artist_id),
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

CREATE TABLE albums
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(128) not null default "",
  album_artist int(64) unsigned,
  FOREIGN KEY (album_artist)
    REFERENCES artists(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

GRANT SELECT ON audioid.albums TO 'audioid_user'@'localhost';

CREATE TABLE songs_albums
(
  song_id int(64) unsigned not null,
  album_id int(64) unsigned not null,
  track_number int(64) unsigned not null,
  CONSTRAINT s_al_pkey PRIMARY KEY (song_id, album_id),
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

CREATE TABLE genres
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(64) not null default ""
);

GRANT SELECT ON audioid.genres TO 'audioid_user'@'localhost';

CREATE TABLE songs_genres
(
  song_id int(64) unsigned not null,
  genre_id int(64) unsigned not null,
  CONSTRAINT s_g_pkey PRIMARY KEY (song_id, genre_id),
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

DELIMITER //

CREATE FUNCTION catalog_path_is_used(in_catalog_path VARCHAR(1024))
RETURNS INT(1) unsigned
BEGIN
  DECLARE wild_in_path VARCHAR(1025);
  DECLARE path_count   INT(64) unsigned;
  DECLARE last_char VARCHAR(1);
  
  SET last_char = SUBSTR(in_catalog_path, LENGTH(in_catalog_path), 1);
  
  IF last_char != '/' THEN
    SET in_catalog_path = CONCAT(in_catalog_path, '/');
  END IF;
  
  SET wild_in_path = CONCAT(in_catalog_path, '%');
  
  SELECT COUNT(base_path) INTO path_count FROM catalogs WHERE base_path LIKE wild_in_path OR in_catalog_path LIKE CONCAT(base_path, '%');
  
  CASE path_count
    WHEN 0 THEN RETURN 0;
    ELSE RETURN 1;
  END CASE;
END//

DELIMITER ;

GRANT EXECUTE ON FUNCTION audioid.catalog_path_is_used TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE insert_catalog(IN in_catalog_name varchar(64), IN in_catalog_base_path VARCHAR(1024))
BEGIN
  DECLARE last_char VARCHAR(1);
  
  SET last_char = SUBSTR(in_catalog_base_path, LENGTH(in_catalog_base_path), 1);
  
  IF last_char != '/' THEN
    SET in_catalog_base_path = CONCAT(in_catalog_base_path, '/');
  END IF;
  
  IF catalog_path_is_used(in_catalog_base_path) = 0 THEN
    INSERT INTO catalogs (name, base_path) VALUES(in_catalog_name, in_catalog_base_path);
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.insert_catalog TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE get_catalog_properties(IN in_catalog_id INT(64) UNSIGNED, OUT out_catalog_name varchar(64), OUT out_catalog_base_path varchar(1024))
BEGIN
  SELECT name, base_path INTO out_catalog_name, out_catalog_base_path FROM catalogs WHERE id = in_catalog_id;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.get_catalog_properties TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE FUNCTION update_catalog(in_catalog_id INT(64) UNSIGNED, in_catalog_name varchar(64), in_catalog_base_path varchar(1024))
RETURNS INT(1) unsigned
BEGIN
  IF catalog_path_is_used(in_catalog_base_path) = 0 THEN
    UPDATE catalogs SET name = in_catalog_name, base_path = in_catalog_base_path WHERE id = in_catalog_id;
    RETURN 1;
  END IF;
  
  RETURN 0;
END//

DELIMITER ;

GRANT EXECUTE ON FUNCTION audioid.update_catalog TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE get_song_id(IN in_song_name VARCHAR(128), IN in_filename VARCHAR(1024), IN in_year int(16) unsigned, IN in_catalog_id int(64) unsigned,
                             IN in_genre_name VARCHAR(64),
                             IN in_album_name VARCHAR(128), IN in_album_artist_name VARCHAR(128), IN in_track_number INT(64) unsigned,
                             OUT out_song_id INT(64) unsigned, OUT out_song_was_inserted BOOL)
get_song_id:BEGIN
  DECLARE var_song_id  INT(64) unsigned DEFAULT NULL;
  DECLARE var_genre_id INT(64) unsigned DEFAULT NULL;
  DECLARE var_album_id INT(64) unsigned DEFAULT NULL;
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  SELECT id INTO var_song_id FROM songs WHERE filename = in_filename;
  
  IF var_song_id IS NOT NULL THEN
    SET out_song_id           = var_song_id;
    SET out_song_was_inserted = 0;
    LEAVE get_song_id;
  END IF;
  
  INSERT INTO songs (name, filename, year, catalog_id) VALUES(in_song_name, in_filename, in_year, in_catalog_id);
  SELECT LAST_INSERT_ID() INTO var_song_id;
  
  IF in_genre_name IS NOT NULL THEN
    SELECT get_genre_id(in_genre_name) INTO var_genre_id;
    INSERT INTO songs_genres (song_id, genre_id) VALUES(var_song_id, var_genre_id);
  END IF;
  
  IF in_album_name IS NOT NULL THEN
    SELECT get_album_id(in_album_name, in_album_artist_name) INTO var_album_id;
    INSERT INTO songs_albums (song_id, album_id, track_number) VALUES(var_song_id, var_album_id, in_track_number);
  END IF;
  
  IF var_rollback = 1 THEN
    ROLLBACK;
    SET out_song_id           = NULL;
    SET out_song_was_inserted = 0;
   ELSE
    COMMIT;
    SET out_song_id = var_song_id;
    SET out_song_was_inserted = 1;
  END IF;
END//

CREATE FUNCTION get_genre_id(in_genre_name VARCHAR(64))
RETURNS INT(64) unsigned
BEGIN
  DECLARE var_gernre_id INT(64) unsigned DEFAULT NULL;
  
  SELECT id INTO var_gernre_id FROM genres WHERE name = in_genre_name;
  
  IF var_gernre_id IS NOT NULL THEN
    RETURN var_gernre_id;
  END IF;
  
  INSERT INTO genres (name) VALUES(in_genre_name);
  
  SELECT LAST_INSERT_ID() INTO var_gernre_id;
  
  RETURN var_gernre_id;
END//

CREATE FUNCTION get_album_id(in_album_name VARCHAR(128), in_album_artist_name VARCHAR(128))
RETURNS INT(64) unsigned
BEGIN
  DECLARE var_album_id  INT(64) unsigned DEFAULT NULL;
  DECLARE var_artist_id INT(64) unsigned DEFAULT NULL;
  
  IF in_album_artist_name IS NULL THEN
    SELECT id INTO var_album_id FROM albums WHERE name = in_album_name AND album_artist IS NULL;
  ELSE
    SELECT id INTO var_artist_id FROM artists WHERE name = in_album_artist_name;
    IF var_artist_id IS NOT NULL THEN
      SELECT id INTO var_album_id FROM albums WHERE name = in_album_name AND album_artist = var_artist_id;
    END IF;
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

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.get_song_id TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE link_song_to_artist(in_artist_name VARCHAR(128), in_song_id INT(64) unsigned, in_list_order INT(4) unsigned, in_conjunction VARCHAR(24), OUT out_success BOOL)
link_song_to_artist:BEGIN
  DECLARE var_artist_id INT(64) unsigned DEFAULT NULL;
  DECLARE var_rollback  BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  IF in_song_id IS NULL OR in_list_order IS NULL OR in_conjunction IS NULL THEN
    SET out_success = 0;
    LEAVE link_song_to_artist;
  END IF;
  
  START TRANSACTION;
  
  SELECT id INTO var_artist_id FROM artists WHERE name = in_artist_name;
  
  IF var_artist_id IS NULL THEN
    INSERT INTO artists (name) VALUES(in_artist_name);
    SELECT LAST_INSERT_ID() INTO var_artist_id;
  END IF;
  
  INSERT INTO songs_artists (song_id, artist_id, list_order, conjunction) VALUES(in_song_id, var_artist_id, in_list_order, in_conjunction);
  
  IF var_rollback THEN
    ROLLBACK;
    SET out_success = 0;
  ELSE
    COMMIT;
    SET out_success = 1;
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.link_song_to_artist TO 'audioid_admin'@'localhost';

DELIMITER //

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
    SELECT DISTINCT s_a.artist_id
    FROM songs_artists AS s_a
    INNER JOIN songs AS s ON s.id = s_a.song_id
      AND s.catalog_id != in_catalog_id
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
    SELECT s_a.album_id
    FROM songs_albums AS s_a
    INNER JOIN songs AS s ON s.id = s_a.song_id
      AND s.catalog_id != in_catalog_id
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

CREATE PROCEDURE delete_song(IN in_song_id INT(64) unsigned, OUT out_success BOOL)
delete_song:BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  SET out_success = 1;
  
  START TRANSACTION;
  
  DELETE FROM songs_albums  WHERE song_id = in_song_id;
  DELETE FROM songs_artists WHERE song_id = in_song_id;
  DELETE FROM songs_genres  WHERE song_id = in_song_id;
  DELETE FROM songs         WHERE id      = in_song_id;
  
  IF var_rollback THEN
    SET out_success = 0;
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
  
  DECLARE var_id INT(64) UNSIGNED;
  DECLARE var_loop_done BOOL DEFAULT FALSE;
  DECLARE var_al_cur CURSOR FOR SELECT a.id FROM albums  AS a LEFT JOIN songs_albums  AS s_a ON s_a.album_id  = a.id GROUP BY a.id HAVING COUNT(s_a.song_id) = 0;
  DECLARE var_ar_cur CURSOR FOR SELECT a.id FROM artists AS a LEFT JOIN songs_artists AS s_a ON s_a.artist_id = a.id GROUP BY a.id HAVING COUNT(s_a.song_id) = 0;
  DECLARE var_g_cur  CURSOR FOR SELECT g.id FROM genres  AS g LEFT JOIN songs_genres  AS s_g ON s_g.genre_id  = g.id GROUP BY g.id HAVING COUNT(s_g.song_id) = 0;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET var_loop_done = TRUE;
  # apparently, MySQL throws an error (well... warning 1329, which has a Level of "Error") if the SELECT statement used in a cursor returns an empty set, instead of just using the NOT FOUND handler.  \-:
  DECLARE CONTINUE HANDLER FOR 1329 SET var_loop_done = TRUE;
  
  OPEN var_al_cur;
  
  album_loop:LOOP
    FETCH var_al_cur INTO var_id;
    IF var_loop_done THEN
      LEAVE album_loop;
    END IF;
    
    DELETE FROM albums WHERE id = var_id;
    
  END LOOP;
  
  CLOSE var_al_cur;
  SET var_loop_done = FALSE;
  OPEN var_ar_cur;
  
  artist_loop:LOOP
    FETCH var_ar_cur INTO var_id;
    
    IF var_loop_done THEN
      LEAVE artist_loop;
    END IF;
    
    DELETE FROM artists WHERE id = var_id;
    
  END LOOP;
  
  CLOSE var_ar_cur;
  SET var_loop_done = FALSE;
  OPEN var_g_cur;
  
  genre_loop:LOOP
    FETCH var_g_cur INTO var_id;
    
    IF var_loop_done THEN
      LEAVE genre_loop;
    END IF;
    
    DELETE FROM genres WHERE id = var_id;
    
  END LOOP;
  
  CLOSE var_g_cur;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.clean_unused_data TO 'audioid_admin'@'localhost';