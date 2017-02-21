<?php // >

set_time_limit(0);

gc_enable();

include_once('php/utils/getid3/getid3.php');

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
  
  $artist_separators = explode('|', $data['artist_separators']);
  
  add_status('attempting to start dir scan...', $session_id);
  $base_dir = $sql_catalog['base_path'];
  scan_directory($base_dir, $cat_id, $cat_name, $artist_separators, $sql_link, $session_id);
  
  add_status('',      $session_id);
  add_status('done.', $session_id);
  
  return $cat_id;
}

//// scanning steps ////

function scan_directory($dir_name, $cat_id, $cat_name, $artist_separators, $sql_link, $session_id)
{
  // a little piece of data mistrust
  if (preg_match('/^[a-zA-Z0-9_]*:\/\//', $dir_name) === 1)
  {
    add_status("invalid dir name. (found \"$dir_name\".)", $session_id);
    return;
  }
  
  $dir_contents = scandir($dir_name);
  add_status("scanning the contents of \"$dir_name\"...", $session_id);
  
  if ($dir_contents === false || !is_array($dir_contents))
  {
    add_status('failed to get contents for "' . $dir_name . '"; skipping it.', $session_id);
    return;
  }
  
  for ($i = 0; $i < count($dir_contents); $i++)
  {
    // ignore current dir & parent dir
    if (strcmp($dir_contents[$i], '.') == 0 || strcmp($dir_contents[$i], '..') == 0)
    {
      continue;
    }
    
    $full_fn = $dir_name . '/' . $dir_contents[$i];
    $status  = 'looking at "' . $full_fn . '"; ';
    
    if (is_dir($full_fn))
    {
      scan_directory($full_fn, $cat_id, $cat_name, $artist_separators, $sql_link, $session_id);
      continue;
    }
    
    if (strcmp(substr($full_fn, strlen($full_fn) - 4), '.mp3') != 0)
    {
      add_status($status . "it's not an mp3 or a dir; ignoring it...", $session_id);
      continue;
    }
    
    add_status($status . "it's an mp3; parsing it...", $session_id);
    
    parse_mp3($cat_id, $full_fn, $artist_separators, $sql_link, $session_id);
  }
}

function parse_mp3($cat_id, $filename, $artist_separators, $sql_link, $session_id)
{
  add_status('parsing ' . $filename, $session_id);
  
  $tags   = get_tags($filename, $artist_separators, $session_id);
  
  $title  = $tags['title'];
  $artist = $tags['artist'];
  $album  = $tags['album'];
  $track  = $tags['track'];
  $genre  = $tags['genre'];
  
  add_status('parsed and validated metadata:', $session_id);
  add_status("title:  $title", $session_id);
  add_status('artists:', $session_id);
  for($i = 0; $i < count($tags['artist_info']['names']); ++$i)
  {
    add_status('  --' . $tags['artist_info']['names'][$i], $session_id);
  }
  add_status("album:  $album", $session_id);
  add_status("track:  $track", $session_id);
  add_status("genre:  $genre", $session_id);
  
  add_status('', $session_id);
  
  insert_song($cat_id, $title, $filename, $tags['artist_info']['names'], $tags['artist_info']['tag_joins'], $album, $track, $genre, $sql_link, $session_id);
  
  $cycles       = gc_collect_cycles();
  $old_contents = file_get_contents('/var/log/my_music/gc.log');
  
  if ($old_contents === false)
    $old_contents = '';
  else
    $old_contents .= "\n";
  
  add_status('', $session_id);
  
  file_put_contents('/var/log/my_music/gc.log', $old_contents . $title . ': ' . $cycles);
}

function insert_song($cat_id, $song_title, $filename, $artists, $artist_joins, $album_name, $track, $genre_name, $sql_link, $session_id)
{
  add_status("inserting $song_title into the database...", $session_id);
  
  // make sure this song isn't already in the db
  {
    add_status("checking preexistence...", $session_id);
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
    add_status("evalutating genre...", $session_id);
    if (isset($genre_name))
    {
      $sql_params = array(':genre_name' => $genre_name);
      $query      = 'SELECT id FROM genres WHERE name=:genre_name ORDER BY id ASC;';
      $sql_genre  = $sql_link->prepare($query);
      $result     = $sql_genre->execute($sql_params);
      if ($result === false)
      {
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2], $session_id);
      }
      else if ($sql_genre->rowCount() == 0)
      {
        $query  = 'INSERT INTO genres (name) VALUES(:genre_name);';
        $result = $sql_link->prepare($query);
        $result = $result->execute($sql_params);
        if ($result === false)
        {
          add_status('query "' . $query . '" died; failed to add genre "' . $genre_name . '": ' . $sql_link->errorInfo()[2], $session_id);
        }
        else
        {
          $genre_id = $sql_link->lastInsertId();
        }
      }
      else if ($sql_genre->rowCount() >= 1)
      {
        $genre = $sql_genre->fetch(PDO::FETCH_ASSOC);
        $genre_id  = $genre['id'];
        
        if ($sql_genre->rowCount() > 1)
          add_status('found ' . $sql_genre->rowCount() . ' genres called "' . $genre_name . '"; using the first one...', $session_id);
      }
    }
  }
  
  // insert the song
  {
    add_status("adding the song...", $session_id);
    $sql_params = array(':song_title' => $song_title);
    $query      = 'INSERT INTO songs (name, filename, catalog_id) ' .
                  'VALUES(:song_title, "' . $filename . '", ' . $cat_id . ');';
    $sql_stmt   = $sql_link->prepare($query);
    $result     = $sql_stmt->execute($sql_params);
    if ($result === false)
    {
      $message = "query \"$query\" died: " . $sql_stmt->errorInfo()[2];
      add_status($message, $session_id);
      die($message);
    }
    
    $song_id = $sql_link->lastInsertId();
    
    if (isset($song_id) && isset($genre_id))
    {
      $query  = "INSERT INTO songs_genres (song_id, genre_id) VALUES($song_id, $genre_id);";
      $result = $sql_link->query($query);
      if ($result === false)
      {
        add_status("query '$query' died: " . $sql_link->errorInfo()[2]);
        die();
      }
    }
  }
  
  // if i have artist info, insert it & associate it with the song
  for ($i = 0; $i < count($artists); ++$i)
  {
    $artist_name = $artists[$i];
    add_status("looking at artist '$artist_name'...", $session_id);
    
    if (isset($artist_name))
    { // get artist info so i can associate the current song w/ it
      $sql_params  = array(':artist_name' => $artist_name);
      $query       = 'SELECT id FROM artists WHERE name=:artist_name ORDER BY id ASC;';
      $sql_artists = $sql_link->prepare($query);
      $result      = $sql_artists->execute($sql_params);
      if ($result === false)
      { // failed to get artist info
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
      }
      else if ($sql_artists->rowCount() == 0)
      { // first time dealing w/ this artist; insert a new row into the table
        $query    = 'INSERT INTO artists (name) VALUES(:artist_name);';
        $sql_stmt = $sql_link->prepare($query);
        $result   = $sql_stmt->execute($sql_params);
        
        if ($result === false)
          add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
        else
          $artist_id = $sql_link->lastInsertId();
      }
      else if ($sql_artists->rowCount() >= 1)
      { // seen this artist before; get its id
        $artist    = $sql_artists->fetch(PDO::FETCH_ASSOC);
        $artist_id = $artist['id'];
        
        if ($sql_artists->rowCount() > 1)
          add_status('found ' . $sql_artists->rowCount() . " artists called \"$artist_name\"; using the first one...", $session_id);
      }
    }
    
    if (isset($artist_id) && is_numeric($artist_id))
    {
      $conjunction = array_key_exists($i, $artist_joins) ? $artist_joins[$i] : "";
      add_status("--joining '$artist_name' to the next with '$conjunction'...", $session_id);
      
      $sql_params  = array(':conjunction' => $conjunction);
      $query       = "INSERT INTO songs_artists (song_id, artist_id, conjunction, list_order) VALUES($song_id, $artist_id, :conjunction, $i);";
      $sql_stmt    = $sql_link->prepare($query);
      $result      = $sql_stmt->execute($sql_params);
      if ($result === false)
        add_status('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
    }
  }
  
  // if i have album info, insert it & associate it with the song
  {
    add_status("checking the album...", $session_id);
    if (isset($album_name))
    { // get album info so i can associate the current song w/ it
      $sql_params = array(':album_name' => $album_name);
      $query      = 'SELECT id FROM albums WHERE name=:album_name ORDER BY id ASC;';
      $sql_albums = $sql_link->prepare($query);
      $result     = $sql_albums->execute($sql_params);
      if ($result === false)
      { // failed to get album info
        add_status('query "' . $query . '" died: ' . $sql_albums->errorInfo()[2]);
      }
      else if ($sql_albums->rowCount() == 0)
      { // first time dealing w/ this album; insert a new row into the table
        $query    = 'INSERT INTO albums (name) VALUES(:album_name);';
        $sql_stmt = $sql_link->prepare($query);
        $result   = $sql_stmt->execute($sql_params);
        
        if ($result === false)
          add_status('query "' . $query . '" died: ' . $sql_stmt->errorInfo()[2]);
        else
          $album_id = $sql_link->lastInsertId();
        
      }
      else if ($sql_albums->rowCount() >= 1)
      { // seen this artist before; get its id
        $album    = $sql_albums->fetch(PDO::FETCH_ASSOC);
        $album_id = $album['id'];
        
        if ($sql_albums->rowCount() > 1)
          add_status('found ' . $sql_albums->rowCount() . ' albums called "' . $album_name . '"; using the first one...', $session_id);
      }
    }
    
    if (isset($album_id) && is_numeric($album_id))
    {
      add_status("setting the track number...", $session_id);
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

function get_tags($filename, $artist_separators)
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
  
  get_clean_title($tags, $filename);
  get_clean_artist($tags, $artist_separators);
  get_clean_album($tags);
  get_track_number($tags, $version, $v1tags, $v2tags);
  get_clean_genre($tags);
  
  return $tags;
}

function get_clean_title(&$tags, $filename)
{
  if (!isset($tags['title']) || strlen($tags['title']) == 0)
  {
    // got no title; pull from the filename
    $tmp           = explode('/', $filename);
    $tags['title'] = $tmp[count($tmp) - 1]; // leave the .mp3 on the end?  sure. why not?
  }
  else
  {
    $tags['title'] = clean_tag($tags['title']);
  }
}

function get_clean_artist(&$tags, $artist_separators)
{
  if (isset($tags['artist']))
  {
    if (strlen($tags['artist']) == 0)
    {
      unset($tags['artist']);
    }
    else
    {
      $tags['artist_info'] = split_tag($tags['artist'], $artist_separators, 'artists');
    }
  }
}

function get_clean_album(&$tags)
{
  if (isset($tags['album']))
  {
    if (strlen($tags['album']) == 0)
      unset($tags['album']);
    else
      $tags['album'] = clean_tag($tags['album']);
  }
}

function get_track_number(&$tags, $version, $v1tags, $v2tags)
{
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
  
  if (isset($tags['track']))
  {
    if (is_numeric($tags['track']))
    {
      $tags['track'] = intval($tags['track']);
    }
    else
    {
      $tags['track'] = clean_tag($tags['track']);
      
      if (is_numeric($tags['track']))
      {
        $tags['track'] = intval($tags['track']);
      }
      else if (isset($tags['album']))
      {
        if (preg_match('/^[0-9]+\/[0-9]+$/', $track) === 1) // if someone put a track as <track number>/<total tracks on the album>, get just the <track number>
        {
          $tmp   = explode('/', $tags['track']);
          $tmp   = $tmp[0];
          $tags['track'] = intval($tmp);
        }
        else // got a valid album but not a valid track number; default to 0
        {
          $tags['track'] = 0;
        }
      }
    }
  }
}

function get_clean_genre(&$tags)
{
  if (isset($tags['genre']))
  {
    $tmp = substr($tags['genre'], 1, strlen($tags['genre']) - 2); // if $tags['genre'] is '(nnn)' where each n is a digit, just wanna use nnn as a genre id.
    if (is_numeric($tags['genre']))
      $tags['genre'] = id3_get_genre_name($tags['genre']);
    else if (is_numeric($tmp))
      $tags['genre'] = id3_get_genre_name($tmp);
    else if (strlen($tags['genre']) == 0)
      unset($tags['genre']);
    else // assume $genre is (s'posed to be) a valid genre name.
      $tags['genre'] = clean_tag($tags['genre']);
  }
}

function has_tag($tags, $tag_name)
{
  return (isset($tags[$tag_name]) && strlen($tags[$tag_name]) > 0);
}

function clean_tag($raw_tag)
{
  //*
  $tag1 = $raw_tag;
  
  /*/ cut out the first 2 characters and every other character after that.
  $tag1 = '';
  for ($i = 2; $i < strlen($raw_tag); $i += 2)
    $tag1 .= substr($raw_tag, $i, 1);
  
  //*/
  
  return $tag1;
}

function split_tag($raw_tag, $separators, $tag_type)
{
  $names = array();
  $tag_joins = array();
  if (isset($raw_tag) && strlen($raw_tag) > 0)
  {
    $raw_tag = clean_tag($raw_tag);
    add_status("parsing artists '$raw_tag'...", $session_id);
    
    do
    {
      $min_pos   = strlen($raw_tag) + 1;
      $sep_index = null;
      $pos       = -1;
      for ($i = 0; $i < count($separators); $i++)
      {
        $pos = strpos($raw_tag, $separators[$i]);
        if ($pos !== false && $pos < $min_pos)
        {
          $min_pos   = $pos;
          $sep_index = $i;
        }
      }
      
      if ($sep_index === null)
        break;
      
      $art = substr($raw_tag, 0, $min_pos);
      
      $names[count($names)] = $art;
      $tag_joins[count($tag_joins)] = $separators[$sep_index];
      
      $new_pos = $min_pos + strlen($separators[$sep_index]) ;
      $raw_tag  = substr($raw_tag, $new_pos);
      
      add_status("adding '$art' to the list of $tag_type with conjunction " . $separators[$sep_index] . ".  got '$raw_tag' left...", $session_id);
    }
    while (true);
    
    add_status("adding '$raw_tag' to the list of artists...", $session_id);
    $names[count($names)] = $raw_tag;
  }
  
  $return_values = array('names' => $names, 'tag_joins' => $tag_joins);
  
  return $return_values;
}

$cat_id = start($data, $sql_link, $session_id);

session_start($session_id);

set_time_limit(30);

?>