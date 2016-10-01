<?php // >

function get_song_info($data) // ($offset, $audio_a, $audio_b)
{
  $offset  = $data['offset'];
  
  if (!isset($offset)  || !is_numeric($offset))
    return '"data error (error code 651)"';
  
  $offset  = intval($offset);
  
  $index   = $_SESSION['now_playing']['current'];
  if (!isset($index) || !is_numeric($index))
    return 'null';
  $index   = (intval($index) + $offset);
  
  if ($index < 0 || $index >= count($_SESSION['now_playing']['song_list']))
    return 'null';
  
  $song = $_SESSION['now_playing']['song_list'][$index];
  
  return '{"id": ' . $song['id'] . ', "title": "' . $song['title'] . '", "artist": ' . (!isset($song['artist']) || $song['artist'] == null ? 'null' : '"' . $song['artist'] . '"') . '}';
}

$feedback = get_song_info($data);

?>