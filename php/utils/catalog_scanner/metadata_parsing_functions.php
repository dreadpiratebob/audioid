<?php

include_once('php/utils/catalog_scanner/status_functions.php');

function parse_mp3($filename, $artist_separators, $session_id)
{
  add_status('parsing ' . $filename, $session_id);
  
  $tags          = get_tags($filename);
  $tags['title'] = clean_extra_chars($tags['title']);
  
  // deal w/ artists
  {
    $artist       = $tags['artist'];
    $artist_names = array();
    $artist_joins = array();
    if (isset($artist) && strlen($artist) > 0)
    {
      $artist = clean_extra_chars($artist);
      add_status("parsing artists \"{$artist}\"...", $session_id);
      
      do
      {
        $min_pos   = strlen($artist) + 1;
        $sep_index = null;
        $pos       = -1;
        for ($i = 0; $i < count($artist_separators); $i++)
        {
          $pos = strpos($artist, $artist_separators[$i]);
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
        $artist_joins[count($artist_joins)] = clean_extra_chars($artist_separators[$sep_index]);
        
        $new_pos = $min_pos + strlen($artist_separators[$sep_index]) ;
        $artist  = substr($artist, $new_pos);
        
        add_status("adding '{$art}' to the list of artists.  got '{$artist}' left...", $session_id);
      }
      while (true);
      
      add_status("adding \"{$artist}\" to the list of artists...", $session_id);
      $artist_names[count($artist_names)] = clean_extra_chars($artist);
    }
    
    $tags['artists']['names'] = $artist_names;
    $tags['artists']['joins'] = $artist_joins;
  }
  
  if (isset($tags['album']))
  {
    if (strlen($tags['album']) == 0)
      unset($tags['album']);
    else
      $tags['album'] = clean_extra_chars($tags['album']);
  }
  
  if (isset($tags['album_artist']))
  {
    if (strlen($tags['album_artist']) == 0)
      unset($tags['album_artist']);
    else
      $tags['album_artist'] = clean_extra_chars($tags['album_artist']);
  }
  
  if (isset($tags['track']))
  {
    if (!isset($tags['album']))
    { // got no album; having a track number doesn't make sense.
      unset($tags['track']);
    }
    else if (is_numeric($tags['track']))
    {
      $tags['track'] = intval($tags['track']);
    }
    else if (preg_match('/^[0-9]+\/[0-9]+$/', $tags['track']) === 1) // if someone put a track as <track number>/<total tracks on the album>, get just the <track number>
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
  else if (isset($tags['album']))
  {
    $tags['track'] = 0;
  }
  
  if (isset($tags['genre']))
  {
    $tmp = substr($tags['genre'], 1, strlen($tags['genre']) - 2); // if $tags['genre'] is '(nnn)' where each n is a digit, just wanna use nnn as a genre id.
    if (is_numeric($tags['genre']))
      $tags['genre'] = id3_get_genre_name($tags['genre']);
    else if (is_numeric($tmp))
      $tags['genre'] = id3_get_genre_name($tmp);
    else if (strlen($tags['genre']) == 0)
      unset($tags['genre']);
    else // assume $tags['genre'] is (s'posed to be) a valid genre name.
      $tags['genre'] = clean_extra_chars($tags['genre']);
  }
  
  $metadata = "\ntitle: \"{$tags['title']}\" (" . get_ascii($tags['title']) . ")\nartists:\n";
  
  for ($i = 0; $i < count($artist_names); ++$i)
    $metadata .= "  --\"{$artist_names[$i]}\" (" . get_ascii($artist_names[$i]) . ")\n";
  
  $metadata .=
  implode
  (
    array
    (
      "album: '{$tags['album']}' (" . get_ascii($tags['album']) . ")\n",
      "track: '{$tags['track']}' (" . get_ascii($tags['track']) . ")\n",
      "genre: '{$tags['genre']}' (" . get_ascii($tags['genre']) . ')'
    )
  );
  
  add_status("parsed and validated metadata:{$metadata}", $session_id);
  add_status('', $session_id);
  
  return $tags;
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
  if ($version == 1 && array_key_exists($name, $v1tags))
    $tags[$name]  = $v1tags[$name][0];
  else if (array_key_exists($name, $v2tags))
    $tags[$name]  = $v2tags[$name][0];
  
  if (!has_tag($tags, $name))
  {
    if ($version == 2 && array_key_exists($name, $v2tags))
      $tags[$name]  = $v1tags[$name][0];
    else if (array_key_exists($name, $v1tags))
      $tags[$name]  = $v2tags[$name][0];
  }
  
  return $tags;
}

function has_tag($tags, $tag_name)
{
  return (array_key_exists($tag_name, $tags) && isset($tags[$tag_name]) && strlen($tags[$tag_name]) > 0);
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

?>