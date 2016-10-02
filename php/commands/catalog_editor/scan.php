<?php // >

set_time_limit(0);

// ini_set('memory_limit', 512*1024*1024); // apparently not the right approach; still errors out @ about 1.5 GB of mem usage
gc_enable();

if (isset($_SESSION['scan_status']))
  unset($_SESSION['scan_status']);

$_SESSION['scan_status']['start_time'] = date('Y-m-d H:i:s.u');

$session_id = session_id();
session_write_close();

function start($data, $sql_link, $session_id)
{
  $cat_id = $data['id'];
  if (!isset($cat_id) || !is_numeric($cat_id))
  {
    add_status('data error (error code 31)<br />done.', $session_id);
    return -1;
  }
  
  $query       = "SELECT id, name, base_path FROM catalogs WHERE id=$cat_id;";
  $sql_catalog = $sql_link->query($query);
  if ($sql_catalog === false)
  {
    add_status('query "' . $query . '" died:<br />' . $sql_link->errorInfo()[2] . '<br />done.', $session_id);
    return -1;
  }
  
  if ($sql_catalog->rowCount() != 1)
  {
    add_status('error: found ' . $sql_catalog->rowCount() . ' catalogs.');
    return -1;
  }
  
  $sql_catalog = $sql_catalog->fetch(PDO::FETCH_ASSOC);
  $cat_name    = $sql_catalog['name'];
  
  session_start($session_id);
  if (isset($_SESSION['cat' . $cat_id . 'mp3s']))
    unset($_SESSION['cat' . $cat_id . 'mp3s']);
  
  $_SESSION['scan_status']['name'] = $cat_name;
  session_write_close();
  
  $base_dir = $sql_catalog['base_path'];
  scan_directory($base_dir, $cat_id, $cat_name, $sql_link, $session_id);
  
  add_status('',      $session_id);
  add_status('done.', $session_id);
  
  return $cat_id;
}

//// scanning steps ////

function scan_directory($dir_name, $cat_id, $cat_name, $sql_link, $session_id)
{
  $dir_contents = scandir($dir_name);
  
  if ($dir_contents === false || !is_array($dir_contents))
  {
    add_status('failed to get contents for "' . $dir_name . '"; skipping it.', $session_id);
    return;
  }
  
  for ($i = 0; $i < count($dir_contents); $i++)
  {
    // ignore current dir & parent dir
    if (strcmp($dir_contents[$i], '.') == 0 || strcmp($dir_contents[$i], '..') == 0)
      continue;
    
    $full_fn = $dir_name . '/' . $dir_contents[$i];
    $status  = 'looking at "' . $full_fn . '"; ';
    
    if (is_dir($full_fn))
    {
      add_status($status . "it's a dir; scanning it...", $session_id);
      scan_directory($full_fn, $cat_id, $cat_name, $sql_link, $session_id);
      continue;
    }
    
    if (strcmp(substr($full_fn, strlen($full_fn) - 4, strlen($full_fn)), '.mp3') != 0)
    {
      add_status($status . "it's not an mp3 or a dir; ignoring it...", $session_id);
      continue;
    }
    
    add_status($status . "it's an mp3; parsing it...", $session_id);
    
    parse_mp3($cat_id, $full_fn, $sql_link, $session_id);
  }
}

function parse_mp3($cat_id, $filename, $sql_link, $session_id)
{
  add_status('parsing ' . $filename, $session_id);
  
  $tags        = id3_get_tag($filename);
  $status_tags = print_r($tags, true);
  
  $title       = $tags['title'];
  $artist      = $tags['artist'];
  $album       = $tags['album'];
  $track       = $tags['track'];
  $genre       = $tags['genre'];
  
  if (!isset($title) || strlen($title) == 0)
    $title = 'untitled';
  else
    $title = clean_tag($title, $sql_link);
  
  if (isset($artist))
  {
    if (strlen($artist) == 0)
      unset($artist);
    else
      $artist = clean_tag($artist, $sql_link);
  }

  if (isset($album))
  {
    if (strlen($album) == 0)
      unset($album);
    else
      $album = clean_tag($album, $sql_link);
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
    else
    {
      $track = clean_tag($track, $sql_link);
      if (is_numeric($track))
      {
        $track = intval($track);
      }
      else if (isset($album))
      {
        if (preg_match('/^[0-9]+\/[0-9]+$/', $track) === 1) // if someone put a track as <track number>/<total tracks on the album>, get just the <track number>
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
      $genre = clean_tag($genre, $sql_link);
  }
  
  $metadata = "\n" .
  'title:  ' . $title . "\n" .
  'artist: ' . $artist . "\n" .
  'album:  ' . $album . "\n" .
  'track:  ' . $track . "\n" .
  'genre:  ' . $genre
  ;
  
  add_status('parsed and validated metadata:' . $metadata, $session_id);
  add_status('', $session_id);
  
  insert_song($cat_id, $title, $filename, $artist, "", $album, $track, $genre, $sql_link, $session_id);
  
  $cycles       = gc_collect_cycles();
  $old_contents = file_get_contents('/var/log/my_music/gc.log');
  
  if ($old_contents === false)
    $old_contents = '';
  else
    $old_contents .= "\n";
  
  file_put_contents('/var/log/my_music/gc.log', $old_contents . $title . ': ' . $cycles);
}

function insert_song($cat_id, $song_title, $filename, $artist_name, $artist_join, $album_name, $track, $genre_name, $sql_link, $session_id)
{
  add_status('inserting ' . $song_title . ' by ' . $artist_name . ' into the database...', $session_id);
  
  // make sure this song isn't already in the db
  {
    $query     = 'SELECT id FROM songs WHERE filename="' . $filename . '" AND catalog_id=' . $cat_id . ';';
    $res_songs = $sql_link->query($query);
    if ($res_songs === false)
      die('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    
    if ($res_songs->rowCount() >= 1)
    {
      add_status('this song is already in this catalog. skipping it.', $session_id);
      return;
    }
  }
  
  // check for the genre & insert it if i have one that isn't there.
  {
    if (isset($genre_name))
    {
      $query     = 'SELECT id FROM genres WHERE name="' . $genre_name . '" ORDER BY id ASC;';
      $sql_genre = $sql_link->query($query);
      if ($sql_genre === false)
      {
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2], $session_id);
      }
      else if ($sql_genre->rowCount() == 0)
      {
        $query  = 'INSERT INTO genres (name) VALUES("' . $genre_name . '");';
        $result = $sql_link->query($query);
        if ($result === false)
          add_status('query "' . $query . '" died; failed to add genre "' . $genre_name . '": ' . $sql_link->errorInfo()[2], $session_id);
        else
          $genre_id = $sql_link->insert_id; // ...i think this is right...
      }
      else if ($sql_genre->rowCount() >= 1)
      {
        $sql_genre = $sql_genre->fetch_array(MYSQL_ASSOC);
        $genre_id  = $sql_genre['id'];
        
        if ($sql_genre->rowCount() > 1)
          add_status('found ' . $sql_genre->rowCount() . ' genres called "' . $genre_name . '"; using the first one...', $session_id);
      }
    }
  }
  
  // insert the song
  {
    $query  = 'INSERT INTO songs (title, filename, catalog_id, genre_id) ' .
              'VALUES("' . $song_title . '", "' . $filename . '", ' . $cat_id . ', ' . (isset($genre_id) ? $genre_id : 'NULL') . ');';
    $result = $sql_link->query($query);
    if ($result === false)
      die('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    
    $song_id = $sql_link->insert_id;
  }
  
  // if i have artist info, insert it & associate it with the song
  {
    if (isset($artist_name))
    { // get artist info so i can associate the current song w/ it
      $query       = 'SELECT id FROM artists WHERE name="' . $artist_name . '" ORDER BY id ASC;';
      $sql_artists = $sql_link->query($query);
      if ($sql_artists === false)
      { // failed to get artist info
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
      }
      else if ($sql_artists->rowCount() == 0)
      { // first time dealing w/ this artist; insert a new row into the table
        $query  = 'INSERT INTO artists (name) VALUES("' . $artist_name . '");';
        $result = $sql_link->query($query);
        
        if ($result === false)
          add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
        else
          $artist_id = $sql_link->insert_id;
      }
      else if ($sql_artists->rowCount() >= 1)
      { // seen this artist before; get its id
        $artists   = $sql_artists->fetch_array(MYSQL_ASSOC);
        $artist_id = $artists['id'];
        
        if ($sql_artists->rowCount() > 1)
          add_status('found ' . $sql_artists->rowCount() . ' artists called "' . $artist_name . '"; using the first one...', $session_id);
      }
    }
    
    if (isset($artist_id) && is_numeric($artist_id))
    {
      $query  = 'INSERT INTO songs_artists (song_id, artist_id, conjunction) VALUES(' . $song_id . ', ' . $artist_id . ', "");';
      $result = $sql_link->query($query);
      if ($result === false)
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    }
  }
  
  // if i have album info, insert it & associate it with the song
  {
    if (isset($album_name))
    { // get album info so i can associate the current song w/ it
      $query      = 'SELECT id FROM albums WHERE name="' . $album_name . '" ORDER BY id ASC;';
      $sql_albums = $sql_link->query($query);
      if ($sql_albums === false)
      { // failed to get album info
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
      }
      else if ($sql_albums->rowCount() == 0)
      { // first time dealing w/ this album; insert a new row into the table
        $query  = 'INSERT INTO albums (name) VALUES("' . $album_name . '");';
        $result = $sql_link->query($query);
        
        if ($result === false)
          add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
        else
          $album_id = $sql_link->insert_id;
        
      }
      else if ($sql_albums->rowCount() >= 1)
      { // seen this artist before; get its id
        $album    = $sql_albums->fetch_array(MYSQL_ASSOC);
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
      if ($result === false)
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    }
  }
  
  add_status('done adding ' . $song_title . ' to the database.', $session_id);
}

//// util ////

function add_status($new_status, $session_id)
{
  session_start($session_id);
  $_SESSION['scan_status'][count($_SESSION['scan_status'])] = $new_status;
  session_write_close();
}

function clean_tag($raw_tag, $sql_link)
{
  // cut out the first 2 characters and every other character after that.
  $tag1 = '';
  for ($i = 2; $i < strlen($raw_tag); $i += 2)
    $tag1 .= substr($raw_tag, $i, 1);
  
  // clean the rest of the characters.
  $tag2 = $sql_link->escape_string($tag1);
  
  return $tag2;
}

$cat_id = start($data, $sql_link, $session_id);

session_start($session_id);
echo count($_SESSION['cat' . $cat_id . 'mp3s']);

set_time_limit(30);

?>