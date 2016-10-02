<?php //>

function delete_catalog($data, $sql_link)
{
  //// data validation & cleanup ////
  $cat_id = $data['cat_id'];
  $fb = '';
  
  if (!isset($cat_id) || !is_numeric($cat_id))
    return 'data error (error code 36)<br />';
  
  $cat_id = intval($cat_id);
  
  //// end data validation & cleanup ////
  
  //// deal w/ artists ////
  $query  = "DELETE FROM songs_artists\n" .
            "WHERE song_id IN\n" .
            "(\n" .
            "  SELECT id\n" .
            "  FROM songs\n" .
            '  WHERE songs.catalog_id = ' . $cat_id . "\n" .
            ');';
  $result = $sql_link->query($query);
  if ($result === false)
    die('this query query died:<br />' . str_replace("\n", "<br />\n", str_replace(' ', '&nbsp;', $query)) . "<br />\nwith this error: " . $sql_link->errorInfo()[2]);
  
  $query  = "DELETE FROM artists WHERE id NOT IN\n" .
            "(\n" .
            "  SELECT DISTINCT s_a.artist_id\n" .
            "  FROM songs_artists AS s_a\n" .
            "  INNER JOIN songs AS s ON s.id = s_a.song_id\n" .
            '    AND s.catalog_id != ' . $cat_id . "\n" .
            ');';
  $result = $sql_link->query($query);
  if ($result === false)
    die('this query query died:<br />' . str_replace("\n", "<br />\n", str_replace(' ', '&nbsp;', $query)) . "<br />\nwith this error: " . $sql_link->errorInfo()[2]);
  
  //// deal w/ albums ////
  $query  = "DELETE FROM songs_albums\n" .
            "WHERE song_id IN\n" .
            "(\n" .
            "  SELECT id\n" .
            "  FROM songs\n" .
            '  WHERE songs.catalog_id = ' . $cat_id . "\n" .
            ');';
  $result = $sql_link->query($query);
  if ($result === false)
    die('this query query died:<br />' . str_replace("\n", "<br />\n", str_replace(' ', '&nbsp;', $query)) . "<br />\nwith this error: " . $sql_link->errorInfo()[2]);
  
  $query  = "DELETE FROM albums WHERE id NOT IN\n" .
            "(\n" .
            "  SELECT s_a.album_id\n" .
            "  FROM songs_albums AS s_a\n" .
            "  INNER JOIN songs AS s ON s.id = s_a.song_id\n" .
            '    AND s.catalog_id!= ' . $cat_id . "\n" .
            ');';
  $result = $sql_link->query($query);
  if ($result === false)
    die('this query query died:<br />' . str_replace("\n", "<br />\n", str_replace(' ', '&nbsp;', $query)) . "<br />\nwith this error: " . $sql_link->errorInfo()[2]);
  
  
  //// deal w/ songs ////
  $query  = 'DELETE FROM songs WHERE catalog_id=' . $cat_id . ';';
  $result = $sql_link->query($query);
  if ($result === false)
    die('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
  
  //// deal w/ genres ////
  $query  = "DELETE FROM genres WHERE id NOT IN\n" .
            "(\n" .
            "  SELECT genre_id\n" .
            "  FROM songs\n" .
            '  WHERE catalog_id != ' . $cat_id . "\n" .
            ');';
  $result = $sql_link->query($query);
  if ($result === false)
    die('this query query died:<br />' . str_replace("\n", "<br />\n", str_replace(' ', '&nbsp;', $query)) . "<br />\nwith this error: " . $sql_link->errorInfo()[2]);
  
  //// delete the catalog ////
  $query  = 'DELETE FROM catalogs WHERE id=' . $cat_id . ';';
  $result = $sql_link->query($query);
  if ($result === false)
    die('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
  
  return 'successfully deleted the catalog.';
}

if (isset($_POST) && is_array($_POST) && count($_POST) > 0)
  $feedback .= delete_catalog($_POST, $sql_link);
else if (isset($_GET) && is_array($_GET) && count($_GET) > 0)
  $feedback .= delete_catalog($_GET, $sql_link);

?>