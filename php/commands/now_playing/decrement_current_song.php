<?php // >

function decrement_current_song()
{
  $current = $_SESSION['now_playing']['current'];
  if (!is_numeric($current) && $current !== null)
    $_SESSION['now_playing']['current'] = null;
  
  if ($current === null)
    $_SESSION['now_playing']['current'] = count($_SESSION['now_playing']['song_list']) - 1;
  else if ($current > 0)
    $_SESSION['now_playing']['current'] = (intval($current) - 1);
  else
    $_SESSION['now_playing']['current'] = null;
  
  return ($_SESSION['now_playing']['current'] == null ? 'null' : $_SESSION['now_playing']['current']);
}

$feedback .= decrement_current_song();

?>