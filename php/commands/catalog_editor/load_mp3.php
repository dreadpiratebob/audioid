<?php // >

include_once('php/utils/getid3/getid3.php');

function start($data, $sql_link)
{
  session_start();
  
  $cat_id          = $_SESSION['cat_scanner']['id'];
  $index           = $_SESSION['cat_scanner']['index'];
  $filename        = $_SESSION['cat_scanner']['file_list'][$index];
  $artist_join_txt = $_SESSION['cat_scanner']['artist_join_txt'];
  
  if (!isset($cat_id) || !isset($index) || !isset($filename))
    return "insufficient data.\n";
  
  if ($index >= count($_SESSION['cat_scanner']['file_list']))
    return 'done.';
  
  $_SESSION['cat_scanner']['index'] = $index + 1;
  
  $session_id = session_id();
  session_write_close();
  
  parse_mp3($cat_id, $filename, $sql_link, $session_id);
  
  if ($index < count($_SESSION['cat_scanner']['file_list']) - 1)
  {
    session_start($session_id);
    return 'next';
  }
  else
  {
    add_status('done.', $session_id);
    session_start($session_id);
    unset($_SESSION['cat_scanner']);
    return 'done';
  }
}

function parse_mp3($cat_id, $filename, $sql_link, $session_id)
{
  add_status('parsing ' . $filename, $session_id);
  
  $tags         = get_tags($filename);
  $status_tags  = print_r($tags, true);
  
  $title        = $tags['title'];
  $artist       = $tags['artist'];
  $album        = $tags['album'];
  $album_artist = $tags['album_artist'];
  $track        = $tags['track'];
  $genre        = $tags['genre'];
  
  $title = clean_extra_chars($title);
  
  // deal w/ artists
  {
    $artist_names = array();
    $artist_joins = array();
    if (isset($artist) && strlen($artist) > 0)
    {
      $artist = clean_extra_chars($artist);
      add_status("parsing artists \"{$artist}\"...", $session_id);
      $separators = $_SESSION['cat_scanner']['separators'];
      do
      {
        $min_pos   = strlen($artist) + 1;
        $sep_index = null;
        $pos       = -1;
        for ($i = 0; $i < count($separators); $i++)
        {
          $pos = strpos($artist, $separators[$i]);
          if ($pos !== false && $pos < $min_pos)
          {
            $min_pos   = $pos;
            $sep_index = $i;
          }
        }
        
        if ($sep_index === null)
          break;
        
        $art = substr($artist, 0, $min_pos);
        
        $artist_names[count($artist_names)] = clean_extra_chars($art);
        $artist_joins[count($artist_joins)] = clean_extra_chars($separators[$sep_index]);
        
        $new_pos = $min_pos + strlen($separators[$sep_index]) ;
        $artist  = substr($artist, $new_pos);
        
        add_status("adding '{$art}' to the list of artists.  got '{$artist}' left...", $session_id);
      }
      while (true);
      
      add_status("adding \"{$artist}\" to the list of artists...", $session_id);
      $artist_names[count($artist_names)] = clean_extra_chars($artist);
    }
  }
  
  if (isset($album))
  {
    if (strlen($album) == 0)
      unset($album);
    else
      $album = clean_extra_chars($album);
  }
  
  if (isset($album_artist))
  {
    if (strlen($album_artist) == 0)
      unset($album_artist);
    else
      $album_artist = clean_extra_chars($album_artist);
  }
  
  if (isset($track))
  {
    if (!isset($album))
    { // got no album; having a track number doesn't make sense.
      unset($track);
    }
    else if (is_numeric($track))
    {
      $track = intval($track);
    }
    else if (preg_match('/^[0-9]+\/[0-9]+$/', $track) === 1) // if someone put a track as <track number>/<total tracks on the album>, get just the <track number>
    {
      $tmp   = explode('/', $track);
      $tmp   = $tmp[0];
      $track = intval($tmp);
    }
    else // got a valid album but not a valid track number; default to 0
    {
      $track = 0;
    }
  }
  else if (isset($album))
  {
    $track = 0;
  }
  
  if (isset($genre))
  {
    $tmp = substr($genre, 1, strlen($genre) - 2); // if $genre is '(nnn)' where each n is a digit, just wanna use nnn as a genre id.
    if (is_numeric($genre))
      $genre = id3_get_genre_name($genre);
    else if (is_numeric($tmp))
      $genre = id3_get_genre_name($tmp);
    else if (strlen($genre) == 0)
      unset($genre);
    else // assume $genre is (s'posed to be) a valid genre name.
      $genre = clean_extra_chars($genre);
  }
  
  $metadata = "\ntitle: \"{$title}\" (" . get_ascii($title) . ")\nartists:\n";
  
  for ($i = 0; $i < count($artist_names); ++$i)
    $metadata .= "  --\"{$artist_names[$i]}\" (" . get_ascii($artist_names[$i]) . ")\n";
  
  $metadata .=
  implode
  (
    array
    (
      "album: '{$album}' (" . get_ascii($album) . ")\n",
      "track: '{$track}' (" . get_ascii($track) . ")\n",
      "genre: '{$genre}' (" . get_ascii($genre) . ')'
    )
  );
  
  add_status("parsed and validated metadata:{$metadata}", $session_id);
  add_status('', $session_id);
  
  insert_song($cat_id, $title, $filename, $artist_names, $artist_joins, $album, $album_artist, $track, $genre, $sql_link, $session_id);
  
  return 'done';
}

function insert_song($cat_id, $song_title, $filename, $artist_names, $artist_joins, $album_name, $album_artist, $track, $genre_name, $sql_link, $session_id)
{
  $joined_artists = '';
  if (count($artist_names) > 0)
  {
    $joined_artists = $artist_names[0];
    for ($i = 1; $i < count($artist_names); ++$i)
      $joined_artists .= ' ' . $artist_joins[$i - 1] . ' ' . $artist_names[$i];
  }
  
  add_status("inserting '{$song_title}'" . (strlen($joined_artists) > 0 ? " by {$joined_artists}" : '') . ' into the database...', $session_id);
  
  // make sure this song isn't already in the db
  {
    $query      = "SELECT id FROM songs WHERE filename=:filename AND catalog_id={$cat_id};";
    $stmt       = $sql_link->prepare($query);
    $sql_params = array(':filename' => $filename);
    $res_songs  = $stmt->execute($sql_params);
    dump_query('song id check', $query, $sql_params, $session_id);
    if ($res_songs === false)
      die('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    
    if ($stmt->rowCount() >= 1)
    {
      add_status('this song is already in this catalog. skipping it.', $session_id);
      return;
    }
  }
  
  // insert the song
  {
    $query      = 'INSERT INTO songs (name, filename, catalog_id) ' .
                  "VALUES(:song_title, :filename, {$cat_id});";
    $stmt       = $sql_link->prepare($query);
    $sql_params = array(':song_title' => $song_title, ':filename' => $filename);
    $result     = $stmt->execute($sql_params);
    dump_query('song insertion', $query, $sql_params, $session_id);
    if ($result === false)
    {
      $message = "this query died: {$query}\nerror info:\n{$sql_link->errorInfo()[2]}\n{$sql_link->errorCode()}\n\nparams:\n" . print_r($sql_params, true);
      add_status($message, $session_id);
      die($message);
    }
    
    $song_id = $sql_link->lastInsertId();
  }
  
  // check for the genre & insert it if i have one that isn't there.
  if (isset($genre_name) && strlen($genre_name) > 0)
  {
    $query      = 'SELECT id FROM genres WHERE name=:genre_name ORDER BY id ASC;';
    $sql_genre  = $sql_link->prepare($query);
    $sql_params = array(':genre_name' => $genre_name);
    $result     = $sql_genre->execute($sql_params);
    dump_query('genre id check', $query, $sql_params, $session_id);
    if ($result === false)
    {
      add_status("query \"{$query }\" died: {$sql_link->errorInfo()[2]}", $session_id);
    }
    else if ($sql_genre->rowCount() == 0)
    {
      $query      = 'INSERT INTO genres (name) VALUES(:genre_name);';
      $stmt       = $sql_link->prepare($query);
      $sql_params = array(':genre_name' => $genre_name);
      $result     = $stmt->execute($sql_params);
      dump_query('genre insertion', $query, $sql_params, $session_id);
      if ($result === false)
      {
        add_status("this query died: $query\nfailed to add genre '$genre_name'.\nerror info:\n" . print_r($sql_link->errorInfo(), true) . print_r($stmt->errorInfo(), true) . "\n\nparams:" . print_r($sql_params, true), $session_id);
      }
      else
      {
        $genre_id = $sql_link->lastInsertId();
      }
    }
    else if ($sql_genre->rowCount() >= 1)
    {
      $arr_genre = $sql_genre->fetch(PDO::FETCH_ASSOC);
      $genre_id  = $arr_genre['id'];
      
      if ($sql_genre->rowCount() > 1)
        add_status("found {$sql_genre->rowCount()} genres called \"{$genre_name}\"; using the first one...", $session_id);
    }
    
    if (isset($genre_id))
    {
      $query  = "INSERT INTO songs_genres (song_id, genre_id)\n" .
                "VALUES({$song_id}, {$genre_id})";
      $result = $sql_link->query($query);
      dump_query('songs_genres insertion', $query, array(), $session_id);
      if ($result === false)
        add_status("this query died:\n{$query}\n\ncouldn't link \"{$song_title}\" to \"{$genre_name}\".\n{$sql_link->errorInfo()[2]}", $session_id);
    }
  }
  
  // if i have artist info, insert it & associate it with the song
  {
    if (isset($artist_names) && is_array($artist_names) && count($artist_names) > 0)
    { // get artist info so i can associate the current song w/ it
      foreach ($artist_names as $index => $artist_name)
      {
        $artist_id   = null;
        $query       = 'SELECT id FROM artists WHERE name=:artist_name ORDER BY id ASC;';
        $sql_artists = $sql_link->prepare($query);
        $sql_params  = array(':artist_name' => $artist_name);
        dump_query('artist id check', $query, $sql_params, $session_id);
        $result      = $sql_artists->execute($sql_params);
        if ($result === false)
        { // failed to get artist info
          add_status("this query died: $query\nerror info:\n" . print_r($sql_link->errorInfo(), true) . print_r($sql_artists->errorInfo(), true) . "\n\nparams:" . print_r($sql_params, true), $session_id);
        }
        else if ($sql_artists->rowCount() == 0)
        { // first time dealing w/ this artist; insert a new row into the table
          $query      = 'INSERT INTO artists (name) VALUES(:artist_name);';
          $stmt       = $sql_link->prepare($query);
          $sql_params = array(':artist_name' => $artist_name);
          $result     = $stmt->execute($sql_params);
          dump_query('artist insertion', $query, $sql_params, $session_id);
          if ($result === false)
            add_status("this query died: $query\nerror info:\n" . print_r($sql_link->errorInfo(), true) . print_r($stmt->errorInfo(), true) . "\n\nparams:" . print_r($sql_params, true), $session_id);
          else
            $artist_id = $sql_link->lastInsertId();
        }
        else if ($sql_artists->rowCount() >= 1)
        { // seen this artist before; get its id
          $artists   = $sql_artists->fetch(PDO::FETCH_ASSOC);
          $artist_id = $artists['id'];
          
          if ($sql_artists->rowCount() > 1)
            add_status("found {$sql_artists->rowCount()} artists called \"{$artist_name}\"; using the first one...", $session_id);
        }
        
        if ($artist_id !== null)
        {
          $art_join   = (0 <= $index && $index < count($artist_joins) ? $artist_joins[$index] : '');
          $query      = "INSERT INTO songs_artists (song_id, artist_id, conjunction, list_order) VALUES({$song_id}, {$artist_id}, :art_join, {$index});";
          $stmt       = $sql_link->prepare($query);
          $sql_params = array(':art_join' => $art_join);
          $result     = $stmt->execute($sql_params);
          dump_query('songs_artists insertion', $query, $sql_params, $session_id);
          if ($result === false)
            add_status("query '{$query}' died:\n" . print_r($sql_link->errorInfo(), true) . print_r($stmt->errorInfo(), true));
        }
      }
    }
  }
  
  // if i have album info, insert it & associate it with the song
  {
    if (isset($album_name))
    { // get album info so i can associate the current song w/ it
      $query           = 'SELECT id FROM artists WHERE name=:album_artist_name;';
      $stmt            = $sql_link->prepare($query);
      $sql_params      = array(':album_artist_name' => $album_artist);
      $temp            = $stmt->execute($sql_params);
      $album_artist_id = null;
      dump_query('album artist id check', $query, $sql_params, $session_id);
      if ($temp === false)
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
      else if ($stmt->rowCount() === 1)
        $album_artist_id = $stmt->fetch(PDO::FETCH_ASSOC)['id'];
      else if ($stmt->rowCount() > 1)
        add_status("multiple artists named $artist_name found when looking for the album artist for $album_name.");
      
      $query      = 'SELECT id FROM albums WHERE name=:album_name ORDER BY id ASC;';
      $sql_albums = $sql_link->prepare($query);
      $sql_params = array(':album_name' => $album_name);
      $result     = $sql_albums->execute($sql_params);
      dump_query('album id check', $query, $sql_params, $session_id);
      if ($result === false)
      { // failed to get album info
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
      }
      else if ($sql_albums->rowCount() == 0)
      { // first time dealing w/ this album; insert a new row into the table
        // $album_artist_id might be null; PDO doesn't handle that well.
        // http://stackoverflow.com/questions/1391777/how-do-i-insert-null-values-using-pdo
        $query      = 'INSERT INTO albums (name, album_artist) VALUES(:album_name, :album_artist_id);';
        $result     = $sql_link->prepare($query);
        $sql_params = array(':album_name' => $album_name, ':album_artist_id' => (isset($album_artist_id) ? $album_artist_id : null));
        $result     = $result->execute($sql_params);
        dump_query('album insertion', $query, $sql_params, $session_id);
        if ($result === false)
          add_status("this query died: $query\nerror info:\n" . print_r($sql_link->errorInfo()[2], true) . "\n\nparams:" . print_r($sql_params, true), $session_id);
        else
          $album_id = $sql_link->lastInsertId();
        
      }
      else if ($sql_albums->rowCount() >= 1)
      { // seen this album before; get its id
        $album    = $sql_albums->fetch(PDO::FETCH_ASSOC);
        $album_id = $album['id'];
        
        if ($sql_albums->rowCount() > 1)
          add_status('found ' . $sql_albums->rowCount() . ' albums called "' . $album_name . '"; using the first one...', $session_id);
      }
    }
    
    if (isset($album_id) && is_numeric($album_id))
    {
      if (isset($track) && is_numeric($track))
        $track = intval($track);
      else
        $track = 0;
      
      $query  = 'INSERT INTO songs_albums (song_id, album_id, track_number) VALUES(' . $song_id . ', ' . $album_id . ', ' . $track . ');';
      $result = $sql_link->query($query);
      dump_query('songs_albums insertion', $query, array(), $session_id);
      if ($result === false)
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    }
  }
  
  add_status('done adding ' . $song_title . ' to the database.', $session_id);
}

function get_tags($filename)
{
  $detagger  = new getID3();
  $file_info = $detagger->analyze($filename);
  
  $version   = intval($file_info['GETID3_VERSION']);
  $v1tags    = $file_info['tags']['id3v1'];
  $v2tags    = $file_info['tags']['id3v2'];
  
  $tags      = array();
  $tags      = extract_tag($tags, $version, 'title',        $v1tags, $v2tags);
  $tags      = extract_tag($tags, $version, 'artist',       $v1tags, $v2tags);
  $tags      = extract_tag($tags, $version, 'album',        $v1tags, $v2tags);
  $tags      = extract_tag($tags, $version, 'album_artist', $v1tags, $v2tags);
  $tags      = extract_tag($tags, $version, 'band',         $v1tags, $v2tags);
  $tags      = extract_tag($tags, $version, 'genre',        $v1tags, $v2tags);
  $tags      = extract_tag($tags, $version, 'year',         $v1tags, $v2tags);
  
  if ($version == 1)
    $tags['track']  = $v1tags['track'][0];
  else
    $tags['track']  = $v2tags['track_number'][0];
  
  if (!has_tag($tags, 'track'))
  {
    if ($version == 2)
      $tags['track']  = $v1tags['track'][0];
    else
      $tags['track']  = $v2tags['track_number'][0];
  }
  
  if (!has_tag($tags, 'title'))
  {
    // got no title; pull from the filename
    $tmp           = explode('/', $filename);
    $tags['title'] = $tmp[count($tmp) - 1]; // leave the .mp3 on the end?  sure. why not?
  }
  
  if (has_tag($tags, 'band') && !has_tag($tags, 'album_artist'))
  { // dunno why the getID3 library calls this 'band' and not 'album artist' or 'album_artist'.
    $tags['album_artist'] = $tags['band'];
    unset($tags['band']);
  }
  
  return $tags;
}

function extract_tag($tags, $version, $name, $v1tags, $v2tags)
{
  if ($version == 1)
    $tags[$name]  = $v1tags[$name][0];
  else
    $tags[$name]  = $v2tags[$name][0];
  
  if (!has_tag($tags, $name))
  {
    if ($version == 2)
      $tags[$name]  = $v1tags[$name][0];
    else
      $tags[$name]  = $v2tags[$name][0];
  }
  
  return $tags;
}

function has_tag($tags, $tag_name)
{
  return (isset($tags[$tag_name]) && strlen($tags[$tag_name]) > 0);
}

function clean_extra_chars($raw_tag)
{
  if (strlen($raw_tag) >= 2 && ord(substr($raw_tag, 0, 1)) == 255 && ord(substr($raw_tag, 1, 1)) == 254)
  {
    // strip off the first 2 chars (\255 & \254) & every other remaining one, which'll be a \0.
    $tag1 = '';
    for ($i = 2; $i <= strlen($raw_tag); $i += 2)
      $tag1 += substr($raw_tag, $i, 1);
  }
  else
  {
    $tag1 = $raw_tag;
  }
  
  return $tag1;
}

function get_ascii($str)
{
  $ord = '';
  for (; strlen($str) > 0; $str = substr($str, 1))
    $ord .= (ord($str) . '.');
  
  return $ord;
}

function add_status($new_status, $session_id, $dump_to_screen = true)
{
  session_start($session_id);
  $_SESSION['scan_log'][count($_SESSION['scan_log'])] = $new_status;
  if ($dump_to_screen)
    $_SESSION['scan_status'][count($_SESSION['scan_status'])] = $new_status;
  
  session_write_close();
}

function dump_query($title, $query, $params, $session_id)
{
  $deparamed_query = $query;
  foreach ($params as $param => $value)
    $deparamed_query = str_replace($param, "\"$value\"", $deparamed_query);
  
  $log_message = "\n\n----query dump: $title ----\nquery w/ params:\n$query\n\nquery w/o params:\n$deparamed_query\n\nparams:\n" . print_r($params, true) . "----end query dump: $title ----\n\n";
  add_status($log_message, $session_id, false);
}

// this attempt at error handling doesn't seem to be working.
set_error_handler
(
  function($code, $string, $file, $line)
  {
    if ($code != 8)
      echo 'error #' . $code . ': ' . $string . "<br />\n<br />\nin " . $file . ' on line ' . $line . "\n";
  }
);

register_shutdown_function
(
  function()
  {
    $feedback .= print_r(error_get_last(), true);
  }
);

$feedback .= start($data, $sql_link);

?>