<?php

function insert_song($cat_id, $song_name, $filename, $year, $artist_names, $artist_joins, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id)
{
  insert_song_data($cat_id, $song_name, $filename, $year, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id, $song_id, $inserted);
  
  if (!$inserted)
    return;
  
  insert_artist_data($song_id, $artist_names, $artist_joins, $sql_link, $session_id);
  add_status("done adding {$song_name} to the database.", $session_id);
}

function insert_song_data($cat_id, $song_name, $filename, $year, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id, &$song_id, &$inserted)
{
  // ':year' isn't a parameter in the SQL below because i'm trusting that the string 'NULL' and any result of the intval function are good values to stick in the middle of a SQL query.
  if (is_numeric($year))
  {
    $year = intval($year);
  }
  else
  {
    $year = 'NULL';
  }
  
  add_status("inserting '{$song_name}'" . (strlen($joined_artists) > 0 ? " by {$joined_artists}" : '') . ' into the database...', $session_id);
  $song_id    = null;
  $query      = "CALL get_song_id(:song_name, :filename, {$year}, {$cat_id}, :genre_name, :album_name, :album_artist_name, :track_number, @song_id, @song_was_inserted);";
  $stmt       = $sql_link->prepare($query);
  $sql_params = array(':song_name' => $song_name, ':filename' => $filename, ':genre_name' => $genre_name, ':album_name' => $album_name, ':album_artist_name' => $album_artist, ':track_number' => $track);
  $result     = $stmt->execute($sql_params);
  dump_query('song insertion', $query, $sql_params, $session_id, true);
  if ($result === false)
  {
    $message = "this query died: {$query}\nerror info:\n{$stmt->errorInfo()[2]}\n{$stmt->errorCode()}\n\nparams:\n" . print_r($sql_params, true);
    add_status($message, $session_id);
    die($message);
  }
  
  // it's kinda annoying that i can't execute multiple queries with one call to the PDO::execute function.
  $query      = 'SELECT @song_id AS song_id, @song_was_inserted AS song_was_inserted;';
  $stmt       = $sql_link->query($query);
  $arr_result = $stmt->fetch(PDO::FETCH_ASSOC);
  $song_id    = $arr_result['song_id'];
  $inserted   = ($arr_result['song_was_inserted'] === 0 || $arr_result['song_was_inserted'] === false ? false : true);
  
  if (!$inserted)
  {
    $message = $stmt->errorInfo()[2];
    if (isset($message))
    {
      add_status("this query died:\n{$query}\n\nerror message:\n{$message}", $session_id);
    }
    else
    {
      add_status('the song is already in the database.', $session_id);
    }
    return;
  }
}

function insert_artist_data($song_id, $artist_names, $artist_joins, $sql_link, $session_id)
{
  $joined_artists = '';
  if (count($artist_names) > 0)
  {
    $joined_artists = $artist_names[0];
    for ($i = 1; $i < count($artist_names); ++$i)
      $joined_artists .= ' ' . $artist_joins[$i - 1] . ' ' . $artist_names[$i];
  }
  
  if (isset($artist_names) && is_array($artist_names) && count($artist_names) > 0)
  { // get artist info so i can associate the current song w/ it
    foreach ($artist_names as $index => $artist_name)
    {
      $conjunction = (0 <= $index && $index < count($artist_joins) ? $artist_joins[$index] : '');
      $params      = array(':artist_name' => $artist_name, ':conjunction' => $conjunction);
      $query       = "CALL link_song_to_artist(:artist_name, {$song_id}, {$index}, :conjunction, @success);\nSELECT @success AS success;";
      $stmt        = $sql_link->prepare($query);
      $result      = $stmt->execute($params);
      
      if ($result === false)
      {
        add_status("query {$query} failed:\n{$stmt->errorInfo()[2]}\nparams:\n" . print_r($params, true), $session_id);
      }
      else
      {
        $arr_result = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($arr_result['success'] === false || $arr_result['success'] === 0)
        {
          add_status("failed to add / link the artist {$artist_name} to '{$song_name}'.", $session_id);
        }
      }
    }
  }
}

?>