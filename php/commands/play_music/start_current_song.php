<?php // >

function start_current_song()
{
  $current = $_SESSION['now_playing']['current'];
  if (isset($current) && is_numeric($current))
    return $current;
  
  if (count($_SESSION['now_playing']['song_list']) > 0)
    $_SESSION['now_playing']['current'] = 0;
  else
    $_SESSION['now_playing']['current'] = null;
  
  return ($_SESSION['now_playing']['current'] == null ? 'null' : $_SESSION['now_playing']['current']);
}

$feedback .= start_current_song();

?>