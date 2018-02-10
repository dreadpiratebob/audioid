CREATE DATABASE audioid;

USE audioid;

CREATE TABLE catalogs
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(64) not null,
  base_path varchar(1024)
);

CREATE TABLE songs
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(128) not null default "",
  year int(16) unsigned not null,
  filename varchar(1024) not null,
  catalog_id int(64) unsigned not null,
  FOREIGN KEY (catalog_id)
    REFERENCES catalogs(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE artists
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(128) not null default ""
);

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

CREATE TABLE genres
(
  id int(64) unsigned not null primary key auto_increment,
  name varchar(64) not null default ""
);

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

# change the password here.
CREATE USER 'audioid_user'@'localhost' IDENTIFIED BY 'some password';

DELIMITER //

CREATE PROCEDURE get_catalog_properties(IN in_catalog_id INT(64) UNSIGNED, OUT out_catalog_name varchar(64), OUT out_catalog_base_path varchar(1024), OUT dbg INT)
BEGIN
  SELECT name, base_path INTO out_catalog_name, out_catalog_base_path FROM catalogs WHERE id = in_catalog_id;
  SELECT COUNT(id) INTO dbg FROM catalogs;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.get_catalog_properties TO 'audioid_user'@'localhost';

DELIMITER //

CREATE PROCEDURE delete_catalog(IN in_catalog_id INT(64) UNSIGNED)
BEGIN
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
  
  COMMIT;
END//

DELIMITER ;

GRANT EXECUTE ON PROCEDURE audioid.delete_catalog TO 'audioid_user'@'localhost';