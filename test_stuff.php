<!doctype>
<html>
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
<?php
include_once('php/utils/getid3/getid3.php');
include_once('php/utils/init_db_vars.php');
include_once('php/utils/startup_connections.php');


/** get tagger

$detagger  = new getID3();
$file_info = $detagger->analyze('/data/bkup/music/mp3/rock/pelican/champions of sound 2008/lima bean.mp3');
$tags      = $file_info['tags']['id3v2'];

echo 'title:&nbsp; ' . $tags['title'][0] . "<br />\n";
echo 'artist: ' . $tags['artist'][0] . "<br />\n";
echo 'album:&nbsp; ' . $tags['album'][0] . "<br />\n";
echo 'genre:&nbsp; ' . $tags['genre'][0] . "<br />\n";


echo "<br />\n";
echo "raw data:<br />\n";
echo '<pre>' . print_r($file_info, true) . '</pre><br /><br />';

// end get tagger */

//** mp3 metadata parsing
$_SESSION['cat_scanner']['separators'] = array(' feat. ', ' & ', ', ');

echo 'joins: <pre>' . print_r($_SESSION['cat_scanner']['separators'], true) . "</pre>\n<br />\n";

function parse_mp3($cat_id, $filename, $sql_link, $session_id)
{
  add_status('parsing ' . $filename, $session_id);
  
  $tags        = get_tags($filename);
  $status_tags = print_r($tags, true);
  
  $title       = $tags['title'];
  $artist      = $tags['artist'];
  $album       = $tags['album'];
  $track       = $tags['track'];
  $genre       = $tags['genre'];
  
  $title = clean_tag($title, $sql_link);
  
  // deal w/ artists
  {
    $artist_names = array();
    $artist_joins = array();
    if (isset($artist) && strlen($artist) > 0)
    {
      $artist = clean_extra_chars($artist);
      add_status('parsing artists "' . $artist . '"...', $session_id);
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
        
        $artist_names[count($artist_names)] = clean_tag($art, $sql_link);
        $artist_joins[count($artist_joins)] = clean_tag($separators[$sep_index], $sql_link);
        
        $new_pos = $min_pos + strlen($separators[$sep_index]) ;
        $artist  = substr($artist, $new_pos);
        
        add_status('adding "' . $art . '" to the list of artists.  got "' . $artist . '" left...', $session_id);
      }
      while (true);
      
      add_status('adding "' . $artist . '" to the list of artists...', $session_id);
      $artist_names[count($artist_names)] = clean_tag($artist, $sql_link);
    }
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
      $genre = clean_tag($genre, $sql_link);
  }
  
  $metadata = "\n" .
  'title: "' . $title  . '" (' . get_ascii($title) . ")\n" .
  "artists:\n";
  
  for ($i = 0; $i < count($artist_names); ++$i)
    $metadata .= '  --"' . $artist_names[$i] . '" (' . get_ascii($artist_names[$i]) . ")\n";
  
  $metadata .=
  'album: "' . $album  . '" (' . get_ascii($album) . ")\n" .
  'track: "' . $track  . '" (' . get_ascii($track) . ")\n" .
  'genre: "' . $genre  . '" (' . get_ascii($genre) . ')';
  
  add_status('parsed and validated metadata:' . $metadata, $session_id);
  add_status('', $session_id);
  
  return 'done';
}

function get_tags($filename)
{
  $detagger  = new getID3();
  $file_info = $detagger->analyze($filename);
  
  $version = intval($file_info['GETID3_VERSION']);
  $v1tags  = $file_info['tags']['id3v1'];
  $v2tags  = $file_info['tags']['id3v2'];
  
  $tags    = extract_tag(array(), $version, 'title',  $v1tags, $v2tags);
  $tags    = extract_tag($tags,   $version, 'artist', $v1tags, $v2tags);
  $tags    = extract_tag($tags,   $version, 'album',  $v1tags, $v2tags);
  $tags    = extract_tag($tags,   $version, 'genre',  $v1tags, $v2tags);
  $tags    = extract_tag($tags,   $version, 'year',   $v1tags, $v2tags);
  
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
  
  echo 'version: ' . $version . "<br />\n";
  echo 'track: ' . $tags['track'] . "<br />\n";
  $print_me = print_r($v1tags, true);
  
  echo '(' . strlen($print_me) . ")<br />\n<pre>" . $print_me;
  echo "</pre><br />\n";
  
  $print_me = print_r($v2tags, true);
  
  echo '(' . strlen($print_me) . ")<br />\n<pre>" . $print_me;
  echo "</pre><br />\n";
  
  if (!has_tag($tags, 'title'))
  {
    // got no title; pull from the filename
    $tmp           = explode('/', $filename);
    $tags['title'] = $tmp[count($tmp) - 1]; // leave the .mp3 on the end?  sure. why not?
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

function clean_tag($raw_tag, $sql_link)
{
  $tag = clean_extra_chars($raw_tag);
  $tag = clean_mysql_unsafe_chars($tag, $sql_link);
  
  return $tag;
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
  
  /*
  $tag1 = str_replace(chr(0),   '', $raw_tag);
  $tag1 = str_replace(chr(255), '', $tag1);
  $tag1 = str_replace(chr(254), '', $tag1);
  */
  
  return $tag1;
}

function clean_mysql_unsafe_chars($raw_tag, $sql_link)
{
  // clean the rest of the characters.
  $tag2 = $sql_link->escape_string($raw_tag);
  
  return $tag2;
}

function get_ascii($str)
{
  $ord = '';
  for (; strlen($str) > 0; $str = substr($str, 1))
    $ord .= (ord($str) . '.');
  
  return $ord;
}

function add_status($new_status, $session_id)
{
  echo $new_status . "<br />\n";
}

$session_id = session_id();

parse_mp3(0, '/data/bkup/music/mp3/rock/finntroll/jaktens tid/f--dosagan.mp3', $sql_link, $session_id);
//*/

/** regex stuff... really should've commented on this when i wrote it...
$separators = ' feat. |, | & | vs. ';

$res = preg_match_all('/^[a-zA-Z0-9\.\&_\(\) %,]+(\|[a-zA-Z0-9\.\&_\(\) %,]+)*$/', $separators, $matches);

echo 'matches: ' . ($res === false ? 'false' : $res) . "<br />\n";

$print_me = print_r($matches, true);
$print_me = str_replace(' ', '&nbsp;', $print_me);
$print_me = str_replace("\n", "<br />\n", $print_me);
echo $print_me;
*/
?>
  </body>
</html>