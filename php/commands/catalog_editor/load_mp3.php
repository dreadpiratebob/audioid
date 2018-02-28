<?php // >

include_once('php/utils/getid3/getid3.php');
include_once('php/utils/catalog_scanner/status_functions.php');
include_once('php/utils/catalog_scanner/metadata_parsing_functions.php');
include_once('php/utils/catalog_scanner/song_sql_functions.php');

function start($data, $sql_link)
{
  session_start();
  
  $cat_id          = $_SESSION['cat_scanner']['id'];
  $index           = $_SESSION['cat_scanner']['index'];
  $filename        = $_SESSION['cat_scanner']['file_list'][$index];
  $artist_join_txt = $_SESSION['cat_scanner']['artist_join_txt'];
  
  if (!isset($cat_id) || !isset($index) || !isset($filename))
    return "insufficient data.\n";
  
  if ($index >= count($_SESSION['cat_scanner']['file_list']))
    return 'done.';
  
  $_SESSION['cat_scanner']['index'] = $index + 1;
  
  $session_id = session_id();
  session_write_close();
  
  $tags = parse_mp3($filename, $_SESSION['cat_scanner']['separators'], $session_id);
  insert_song($cat_id, $tags['title'], $filename, $tags['artists']['names'], $tags['artists']['joins'], $tags['album'], $tags['album_artist'], $tags['track'], $tags['genre'], $sql_link, $session_id);
  
  if ($index < count($_SESSION['cat_scanner']['file_list']) - 1)
  {
    session_start($session_id);
    return 'next';
  }
  else
  {
    add_status('done.', $session_id);
    session_start($session_id);
    unset($_SESSION['cat_scanner']);
    return 'done';
  }
}

// this attempt at error handling doesn't seem to be working.
set_error_handler
(
  function($code, $string, $file, $line)
  {
    if ($code != 8)
      echo 'error #' . $code . ': ' . $string . "<br />\n<br />\nin " . $file . ' on line ' . $line . "\n";
  }
);

register_shutdown_function
(
  function()
  {
    $feedback .= print_r(error_get_last(), true);
  }
);

$feedback .= start($data, $sql_link);

?>