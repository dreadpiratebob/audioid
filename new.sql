CREATE USER 'audioid_funcs'@'localhost' IDENTIFIED BY 'run functions all night';

drop function catalog_path_is_used;

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

GRANT EXECUTE ON FUNCTION audioid.catalog_path_is_used TO 'audioid_funcs'@'localhost';
