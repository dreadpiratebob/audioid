<?php

function delete_nonexistent_songs($cat_id, $sql_link, $session_id, $base_path = null)
{
  if ($base_path == null)
  {
    $query     = "SELECT base_path FROM catalogs WHERE id = {$cat_id};";
    $stmt      = $sql_link->query($query);
    $base_path = $stmt->fetch(PDO::FETCH_ASSOC)['base_path'];
  }
  
  $query          = "SELECT id, filename FROM songs WHERE catalog_id = {$cat_id};";
  $stmt           = $sql_link->query($query);
  $deleted_a_song = false;
  
  for ($i = 0; $i < $stmt->rowCount(); ++$i)
  {
    $song_data = $stmt->fetch(PDO::FETCH_ASSOC);
    $message   = "checking file existence for '{$song_data['filename']}'; ";
    if (file_exists(/* $base_path . */$song_data['filename']))
    {
      add_status("{$message}it exists...", $session_id);
      continue;
    }
    
    add_status("{$message}file not found; deleting it...", $session_id);
    $deleted_a_song = true;
    $del_query      = "CALL delete_song({$song_data['id']}, @success);";
    $sql_result     = $sql_link->query($del_query);
    
    $query      = 'SELECT @success AS success;';
    $sql_result = $sql_link->query($query);
    $arr_result = $sql_result->fetch(PDO::FETCH_ASSOC);
    
    if ($arr_result['success'] === 1)
    {
      $arr_result = true;
    }
    else if ($arr_result['success'] === 0)
    {
      $arr_result = false;
    }
    
    if (!$arr_result['success'])
    {
      add_status("failed to delete file '{$song_data['filename']}'.", $session_id);
    }
  }
  
  if (!$deleted_a_song)
  {
    return;
  }
  
  add_status('cleaning extra data...', $session_id);
  
  $query  = "CALL clean_unused_data();";
  $result = $sql_link->query($query);
  
  if ($result === false)
  {
    add_status("query '{$query}' died with this error:\n{$sql_link->errorInfo()[2]}", $session_id);
    return;
  }
  
  $query  = 'SELECT @success AS success';
  $stmt   = $sql_link->query($query);
  $result = $stmt->fetch(PDO::FETCH_ASSOC);
  
  if ($result['success'] === 0)
  {
    $result['success'] = false;
  }
  else if ($result['success'] === 1)
  {
    $result['success'] = true;
  }
  
  if ($result['success'])
  {
    add_status('cleaned extra data.', $session_id);
  }
  else
  {
    add_status('failed to clean extra data.', $session_id);
  }
  
}

function insert_song($cat_id, $song_name, $filename, $year, $artist_names, $artist_joins, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id)
{
  $joined_artists = '';
  if (isset($artist_names) && count($artist_names) > 0)
  {
    $joined_artists = $artist_names[0];
    for ($i = 1; $i < count($artist_names); ++$i)
      $joined_artists .= ' ' . $artist_joins[$i - 1] . ' ' . $artist_names[$i];
  }
  
  insert_song_data($cat_id, $song_name, $filename, $year, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id, $joined_artists, $song_id, $inserted);
  
  if (!$inserted)
    return;
  
  insert_artist_data($song_id, $artist_names, $artist_joins, $sql_link, $session_id);
  add_status("done adding {$song_name} to the database.", $session_id);
}

function insert_song_data($cat_id, $song_name, $filename, $year, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id, $joined_artists, &$song_id, &$inserted)
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
  
  add_status("inserting '{$song_name}'" . (isset($joined_artists) ? " by {$joined_artists}" : '') . ' into the database...', $session_id);
  $song_id    = null;
  $query      = "CALL get_song_id(:song_name, :filename, {$year}, {$cat_id}, :genre_name, :album_name, :album_artist_name, :track_number, @song_id, @song_was_inserted);";
  $stmt       = $sql_link->prepare($query);
  $sql_params = array(':song_name' => $song_name, ':filename' => $filename, ':genre_name' => $genre_name, ':album_name' => $album_name, ':album_artist_name' => $album_artist, ':track_number' => $track);
  $result     = $stmt->execute($sql_params);
  dump_query('song insertion', $query, $sql_params, $session_id);
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
  if (isset($artist_names) && is_array($artist_names) && count($artist_names) > 0)
  { // get artist info so i can associate the current song w/ it
    foreach ($artist_names as $index => $artist_name)
    {
      $conjunction = (0 <= $index && $index < count($artist_joins) ? $artist_joins[$index] : '');
      $params      = array(':artist_name' => $artist_name, ':conjunction' => $conjunction);
      $query       = "CALL link_song_to_artist(:artist_name, {$song_id}, {$index}, :conjunction, @success);";
      $stmt        = $sql_link->prepare($query);
      $result      = $stmt->execute($params);
      
      if ($result === false)
      {
        add_status("query {$query} failed:\n{$stmt->errorInfo()[2]}\nparams:\n" . print_r($params, true), $session_id);
        return;
      }
      
      $query      = 'SELECT @success AS success;';
      $stmt       = $sql_link->query($query);
      $arr_result = $stmt->fetch(PDO::FETCH_ASSOC);
      if ($arr_result['success'] === false || $arr_result['success'] === 0)
      {
        add_status("failed to add / link the artist {$artist_name} to '{$song_name}'.", $session_id);
      }
    }
  }
}

?>