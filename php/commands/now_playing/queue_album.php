<?php // >

function queue_album_up($data, $sql_link)
{
  $id = $data['id'];
  
  if (!isset($id) || !is_numeric($id))
    return "data error (error code 343)";
  
  $id        = intval($id);
  $query     = "SELECT s.id AS id, s.name AS title, s.filename AS filename, GROUP_CONCAT(ar.name, s_ar.conjunction ORDER BY s_ar.list_order SEPARATOR '') AS artist\n" .
               "FROM songs AS s\n" .
               "  INNER JOIN songs_albums AS s_al ON s_al.song_id = s.id\n" .
               "  INNER JOIN albums       AS al   ON al.id = s_al.album_id\n" .
               "    AND al.id = $id\n" .
               "  LEFT JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
               "  LEFT JOIN artists AS ar ON ar.id = s_ar.artist_id\n" .
               "GROUP BY s.id, s.name, s.filename\n" . // gotta have 3 columns here 'cause i can't select columns that i'm not also grouping by.  also, i have to have the 'group by' clause after the 'where' clause.
               "ORDER BY s_al.track_number;";
  $sql_album = $sql_link->query($query);
  
  if ($sql_album === false)
    return 'data error (error code 344: ' . $sql_link->errorInfo()[2] . ')';
  
  for ($i = 0; $i < $sql_album->rowCount(); ++$i)
  {
    $song = $sql_album->fetch(PDO::FETCH_ASSOC);
    $_SESSION['now_playing']['song_list'][count($_SESSION['now_playing']['song_list'])] = $song;
  }
}

echo queue_album_up($data, $sql_link);

?>