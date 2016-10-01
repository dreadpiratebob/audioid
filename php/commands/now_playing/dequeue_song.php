<?php // >

function dequeue_song($data)
{
  $index = $data['index'];
  $id    = $data['id'];
  
  if (!isset($index) || !is_numeric($index) || !isset($id) || !is_numeric($id))
    return 'data error (error code 101)';
  
  $index = intval($index);
  $id    = intval($id);
  $cur   = $_SESSION['now_playing']['current'];
  if (!isset($cur) || !is_numeric($cur))
    $cur = null;
  else
    $cur = intval($cur); // should be unnecessary
  
  if ($_SESSION['now_playing']['song_list'][$index]['id'] != $id)
    return 'data error (error code 102)';
  
  for ($i = $index; $i < count($_SESSION['now_playing']['song_list']); ++$i)
    $_SESSION['now_playing']['song_list'][$i] = $_SESSION['now_playing']['song_list'][$i + 1];
  
  unset($_SESSION['now_playing']['song_list'][count($_SESSION['now_playing']['song_list']) - 1]);
  
  if ($cur != null && $index < $cur)
    $_SESSION['now_playing']['current'] = $cur - 1;
  
  return '';
}

$feedback = dequeue_song($data);

?>