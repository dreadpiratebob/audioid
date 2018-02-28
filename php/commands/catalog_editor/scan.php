<?php // >

include_once('php/utils/catalog_scanner/status_functions.php');
include_once('php/utils/catalog_scanner/status_functions.php');
include_once('php/utils/catalog_scanner/metadata_parsing_functions.php');
include_once('php/utils/catalog_scanner/song_sql_functions.php');

set_time_limit(0);

gc_enable();

include_once('php/utils/getid3/getid3.php');

if (isset($_SESSION['scan_status']))
  unset($_SESSION['scan_status']);

$_SESSION['scan_status']['start_time'] = date('Y-m-d H:i:s.u');

$session_id = session_id();
session_write_close();

function start($data, $sql_link, $session_id)
{
  $cat_id = $data['id'];
  if (!isset($cat_id) || !is_numeric($cat_id))
  {
    add_status('data error (error code 31)<br />done.', $session_id);
    return -1;
  }
  
  $query       = "SELECT id, name, base_path FROM catalogs WHERE id={$cat_id};";
  $sql_catalog = $sql_link->query($query);
  if ($sql_catalog === false)
  {
    add_status("query \"{$query}\" died:<br />{$sql_link->errorInfo()[2]}<br />done.", $session_id);
    return -1;
  }
  
  if ($sql_catalog->rowCount() != 1)
  {
    add_status("error: found {$sql_catalog->rowCount()} catalogs.");
    return -1;
  }
  
  $sql_catalog = $sql_catalog->fetch(PDO::FETCH_ASSOC);
  $cat_name    = $sql_catalog['name'];
  
  session_start($session_id);
  if (isset($_SESSION["cat{$cat_id}mp3s"]))
    unset($_SESSION["cat{$cat_id}mp3s"]);
  
  $_SESSION['scan_status']['name'] = $cat_name;
  session_write_close();
  
  $artist_separators = explode('|', $data['artist_separators']);
  
  add_status('attempting to start dir scan...', $session_id);
  $base_dir = $sql_catalog['base_path'];
  scan_directory($base_dir, $cat_id, $cat_name, $artist_separators, $sql_link, $session_id);
  
  add_status('',      $session_id);
  add_status('done.', $session_id);
  
  return $cat_id;
}

//// scanning steps ////

function scan_directory($dir_name, $cat_id, $cat_name, $artist_separators, $sql_link, $session_id)
{
  add_status('', $session_id);
  
  // a little piece of data mistrust
  if (preg_match('/^[a-zA-Z0-9_]*:\/\//', $dir_name) === 1)
  {
    add_status("invalid dir name. (found \"{$dir_name}\".)", $session_id);
    return;
  }
  
  $dir_contents = scandir($dir_name);
  add_status("scanning the contents of \"{$dir_name}\"...", $session_id);
  
  if ($dir_contents === false || !is_array($dir_contents))
  {
    add_status("failed to get contents for \"{$dir_name}\"; skipping it.", $session_id);
    return;
  }
  
  if (strcmp(substr($dir_name, strlen($dirname) - 1, 1), '/') == 0)
  {
    $dir_name = substr($dir_name, 0, strlen($dir_name) - 1);
  }
  
  for ($i = 0; $i < count($dir_contents); $i++)
  {
    // ignore current dir & parent dir
    if (strcmp($dir_contents[$i], '.') == 0 || strcmp($dir_contents[$i], '..') == 0)
    {
      continue;
    }
    
    $full_fn = "{$dir_name}/{$dir_contents[$i]}";
    $status  = "looking at \"{$full_fn}\"; ";
    
    if (is_dir($full_fn))
    {
      scan_directory($full_fn, $cat_id, $cat_name, $artist_separators, $sql_link, $session_id);
      continue;
    }
    
    if (strcmp(substr($full_fn, strlen($full_fn) - 4), '.mp3') != 0)
    {
      add_status("{$status}it's not an mp3 or a dir; ignoring it...", $session_id);
      continue;
    }
    
    add_status("{$status}it's an mp3; parsing it...", $session_id);
    
    $tags = parse_mp3($full_fn, $artist_separators, $session_id);
    insert_song($cat_id, $tags['title'], $full_fn, $tags['year'], $tags['artists']['names'], $tags['artists']['joins'], $tags['album'], $tags['album_artist'], $tags['track'], $tags['genre'], $sql_link, $session_id);
  }
}

$cat_id = start($data, $sql_link, $session_id);

session_start($session_id);

set_time_limit(30);

?>