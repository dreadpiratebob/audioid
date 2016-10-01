<?php // >

function queue_stuff_up($data, $sql_link)
{
  $id = $data['id'];
  
  if (!isset($id) || !is_numeric($id))
    return "data error (error code 271)";
  
  $id       = intval($id);
  
  $query    = "SELECT s.id AS id, s.title AS title, s.filename AS filename, GROUP_CONCAT(ar.name, s_ar.conjunction ORDER BY s_ar.list_order SEPARATOR '') AS artist\n" .
              "FROM songs AS s\n" .
              "  LEFT JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
              "  LEFT JOIN artists AS ar ON ar.id = s_ar.artist_id\n" .
              'WHERE s.id=' . $id . "\n" .
              "GROUP BY s.id, s.title, s.filename"; // gotta have 3 columns here 'cause i can't select columns that i'm not also grouping by.  also, i have to have the 'group by' clause after the 'where' clause.
  $sql_song = $sql_link->query($query);
  
  if ($sql_song === false)
    return 'data error (error code 272)';
  
  if ($sql_song->num_rows != 1)
    return 'data error (error code 273)';
  
  $song = $sql_song->fetch_array(MYSQL_ASSOC);
  
  $_SESSION['now_playing']['song_list'][count($_SESSION['now_playing']['song_list'])] = $song;
}

echo queue_stuff_up($data, $sql_link);

?>