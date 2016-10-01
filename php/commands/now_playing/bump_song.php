<?php

function bump_song($data)
{
  $index = $data['index'];
  $id    = $data['id'];
  $dir   = $data['dir'];
  $up    = true;
  
  if (!isset($index) || !is_numeric($index) || !isset($id)  || !is_numeric($id) || !isset($dir))
    return 'data error (error code 24576)';
  
  $index = intval($index);
  $id    = intval($id);
  
  if ($index < 0 || $index > count($_SESSION['now_playing']['song_list']))
    return 'data error (error code 24577)';
  
  if ($id != $_SESSION['now_playing']['song_list'][$index]['id'])
    return 'data error (error code 24578)';
  
  if (strcmp($dir, 'down') == 0)
    $up = false;
  else if (strcmp($dir, 'up') != 0)
    return 'data error (error code 24579)';
  
  $tmp = $_SESSION['now_playing']['song_list'][$index];
  if ($up)
  {
    if ($index <= 0)
      return '';
    
    $_SESSION['now_playing']['song_list'][$index] = $_SESSION['now_playing']['song_list'][$index - 1];
    $_SESSION['now_playing']['song_list'][$index - 1] = $tmp;
    
    if ($index === $_SESSION['now_playing']['current'])
      $_SESSION['now_playing']['current'] -= 1;
    else if ($index - 1 === $_SESSION['now_playing']['current'])
      $_SESSION['now_playing']['current'] += 1;
  }
  else
  {
    if ($index >= count($_SESSION['now_playing']['song_list']) - 1)
      return '';
    
    $_SESSION['now_playing']['song_list'][$index] = $_SESSION['now_playing']['song_list'][$index + 1];
    $_SESSION['now_playing']['song_list'][$index + 1] = $tmp;
    
    if ($index === $_SESSION['now_playing']['current'])
      $_SESSION['now_playing']['current'] += 1;
    else if ($index === $_SESSION['now_playing']['current'] - 1)
      $_SESSION['now_playing']['current'] -= 1;
  }
  
  return '';
}

$feedback .= bump_song($data);
echo $feedback;
?>