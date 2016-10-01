<?php
$current = $_SESSION['now_playing']['current'];

if (!isset($current) || $current === null)
{
  echo 'null/null';
}
else
{
  if ($current < count($_SESSION['now_playing']['song_list']))
    echo $_SESSION['now_playing']['song_list'][$current]['id'];
  else
    echo 'null';
  
  echo '/';
  
  if ($current + 1 < count($_SESSION['now_playing']['song_list']))
    echo $_SESSION['now_playing']['song_list'][$current + 1]['id'];
  else
    echo 'null';
}
?>