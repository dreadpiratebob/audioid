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
  catalog_id int(64) unsigned not null,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  UNIQUE(id),
  UNIQUE(catalog_id, name),
  FOREIGN KEY (catalog_id)
    REFERENCES catalogs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
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
  conjunction varchar(64) not null default ", " COLLATE utf8mb4_bin,
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
  catalog_id int(64) unsigned not null,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  album_artist int(64) unsigned,
  UNIQUE(id),
  UNIQUE(catalog_id, name),
  FOREIGN KEY (catalog_id)
    REFERENCES catalogs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
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
  catalog_id int(64) unsigned not null,
  name varchar(1024) not null default "" COLLATE utf8mb4_bin,
  UNIQUE(id),
  UNIQUE(catalog_id, name),
  FOREIGN KEY (catalog_id)
    REFERENCES catalogs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
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

CREATE TABLE song_deletion_whitelist (id int(64) unsigned not null);

GRANT INSERT ON audioid.song_deletion_whitelist TO 'audioid_admin'@'localhost';
GRANT SELECT ON audioid.song_deletion_whitelist TO 'audioid_admin'@'localhost';
GRANT DELETE ON audioid.song_deletion_whitelist TO 'audioid_admin'@'localhost';



DELIMITER //

CREATE PROCEDURE delete_song(IN in_song_id INT(64) unsigned)
delete_song:BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  START TRANSACTION;
  
  DELETE FROM songs_albums    WHERE song_id = in_song_id;
  DELETE FROM songs_artists   WHERE song_id = in_song_id;
  DELETE FROM songs_genres    WHERE song_id = in_song_id;
  DELETE FROM song_similarity WHERE song_id = song1 OR song_id = song2;
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

CREATE PROCEDURE delete_songs_with_filename_whitelist(IN in_catalog_id INT(64) unsigned, IN in_filenames text COLLATE utf8mb4_bin)
delete_song:BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE delimiter VARCHAR(3) DEFAULT ',';
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  START TRANSACTION;
  
  DROP TEMPORARY TABLE IF EXISTS song_deletion_filename_whitelist;
  CREATE TEMPORARY TABLE song_deletion_filename_whitelist(id INT(64) unsigned);
  WHILE LOCATE(delimiter, in_filenames) > 1 DO
    INSERT INTO song_deletion_filename_whitelist SELECT id FROM songs WHERE filename=SUBSTRING_INDEX(in_filenames, delimiter, 1);
    SET in_filenames = REPLACE(in_filenames, (SELECT LEFT(in_filenames, LOCATE(delimiter, in_filenames))), '');
  END WHILE;
  INSERT INTO song_deletion_filename_whitelist SELECT id FROM songs WHERE filename=SUBSTRING_INDEX(in_filenames, delimiter, 1);
  
  DELETE FROM songs_albums  WHERE song_id NOT IN (SELECT id FROM song_deletion_filename_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  DELETE FROM songs_artists WHERE song_id NOT IN (SELECT id FROM song_deletion_filename_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  DELETE FROM songs_genres  WHERE song_id NOT IN (SELECT id FROM song_deletion_filename_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  DELETE FROM songs         WHERE id      NOT IN (SELECT id FROM song_deletion_filename_whitelist) AND catalog_id = in_catalog_id;
  
#  DELETE FROM song_similarity
#  WHERE song1 NOT IN (SELECT fd.id FROM song_deletion_filename_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id)
#     OR song2 NOT IN (SELECT fd.id FROM song_deletion_filename_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  
  IF var_rollback THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.delete_songs_with_filename_whitelist TO 'audioid_admin'@'localhost';

DELIMITER //

CREATE PROCEDURE delete_songs_with_preset_whitelist(IN in_catalog_id INT(64) unsigned)
delete_song:BEGIN
  DECLARE var_rollback BOOL DEFAULT 0;
  DECLARE delimiter VARCHAR(3) DEFAULT ',';
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET var_rollback = 1;
  
  START TRANSACTION;
  
  DELETE FROM songs_albums  WHERE song_id NOT IN (SELECT id FROM song_deletion_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  DELETE FROM songs_artists WHERE song_id NOT IN (SELECT id FROM song_deletion_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  DELETE FROM songs_genres  WHERE song_id NOT IN (SELECT id FROM song_deletion_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  DELETE FROM songs         WHERE id      NOT IN (SELECT id FROM song_deletion_whitelist) AND catalog_id = in_catalog_id;
  
#  DELETE FROM song_similarity
#  WHERE song1 NOT IN (SELECT fd.id FROM song_deletion_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id)
#     OR song2 NOT IN (SELECT fd.id FROM song_deletion_whitelist UNION SELECT id FROM songs WHERE catalog_id != in_catalog_id);
  
  IF var_rollback THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.delete_songs_with_preset_whitelist TO 'audioid_admin'@'localhost';


CREATE FULLTEXT INDEX song_titles ON songs (name);
CREATE FULLTEXT INDEX artist_names ON artists (name);
CREATE FULLTEXT INDEX album_names ON albums (name);
CREATE FULLTEXT INDEX genre_names ON genres (name);

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