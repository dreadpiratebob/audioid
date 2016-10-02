<?php // >

/**** begin util stuff ****/

function get_post_query($data = null)
{
  if ($data == null)
    $data = $_POST;
  
  $post_query = '';
  foreach ($_POST as $key => $value)
    $post_query .= ($key . '=' . $value . '&');
  $post_query = substr($post_query, 0, strlen($post_query) - 1);
  return $post_query;
}

function get_id_from_query($key, $data)
{
  $value = $data[$key];
  if (!isset($data))
    $value = $_POST[$key];
  
  if (isset($value) && $value != null && strlen($value) > 0)
  {
    if (is_numeric($value))
      $value = intval($value);
    else if (preg_match_all('/^[0-9]+(,[0-9]+)+$/', $value, $matches) == 1)
      ; // leave $value alone
    else  
      $value = null;
  }
  else
  {
    $value = null;
  }
  
  return $value;
}

function validate_name_from_data($name)
{
  if (!isset($name))
    return null;
  
  $errors = array
            (
              PREG_NO_ERROR              => 'no error',
              PREG_INTERNAL_ERROR        => 'internal error',
              PREG_BACKTRACK_LIMIT_ERROR => 'backtrack limit error',
              PREG_RECURSION_LIMIT_ERROR => 'recursion limit error',
              PREG_BAD_UTF8_ERROR        => 'bad utf8 error',
              PREG_BAD_UTF8_OFFSET_ERROR => 'bad utf8 offset error'
            );
  
  $reg_match = preg_match_all('/^[A-Za-z0-9&% _À-ÖØ-öø-ÿ]*$/', $name, $matches);
  if ($reg_match === false)
    echo 'regex failed: ' . $errors[preg_last_error()] . "<br />\n";
  
  if ($reg_match !== 1)
    return null;
  
  return $name;
}

function validate_order_by($order_by, $col_dict, $sort_dict = null)
{
  if (!isset($order_by) || strlen($order_by) == 0)
    return array();
  
  if (!isset($sort_dict) || $sort_dict == null || !is_array($sort_dict))
    $sort_dict = array
                 (
                   '+'   => 'ASC', '-'    => 'DESC',
                   'ASC' => 'ASC', 'DESC' => 'DESC'
                 );
  
  $cols      = explode(', ', $order_by);
  $new_order = array();
  for ($c = 0; $c < count($cols); ++$c)
  {
    $col = explode(' ', $cols[$c]);
    if (!isset($col_dict[$col[0]]) || !isset($sort_dict[$col[1]]))
      // got an invalid column; ignore it.
      continue;
    
    $new_order[count($new_order)]['col']       = $col_dict[$col[0]];
    $new_order[count($new_order) - 1]['order'] = $sort_dict[$col[1]];
  }
  
  return $new_order;
}

function get_order_by_string($order_by)
{
  $str = '';
  for ($i = 0; $i < count($order_by); ++$i)
    $str .= $order_by[$i]['col'] . ' ' . $order_by[$i]['order'] . ', ';
  $str = substr($str, 0, strlen($str) - 2);
  
  return $str;
}

function get_pretty_order_by_string($order_by)
{
  $str = '';
  for ($i = 0; $i < count($order_by); ++$i)
  {
    $str .= str_replace('_', ' ', $order_by[$i]['col']);
    $str .= ' ';
    $str .= (strcmp(strtolower($order_by[$i]['order']), 'asc') == 0 ? 'ascending' : 'descending');
    $str .= ', ';
  }
  $str = substr($str, 0, strlen($str) - 2);
  
  return $str;
}

function get_pretty_array($arr)
{
  if (!is_array($arr))
    return false;
  
  $str = print_r($arr, true);
  $str = str_replace(' ', '&nbsp;', $str);
  $str = str_replace("\n", "<br />\n", $str);
  return $str;
}

function get_new_order_by($new_col, $old_order_by)
{
  if (strcmp($old_order_by[0]['col'], $new_col) == 0)
  {
    if (strcmp($old_order_by[0]['order'], 'ASC') == 0)
      $old_order_by[0]['order'] = 'DESC';
    else
      $old_order_by[0]['order'] = 'ASC';
    
    return $old_order_by;
  }
  
  $found = false;
  for ($i = 1; $i < count($old_order_by); ++$i)
  {
    if (strcmp($old_order_by[$i]['col'], $new_col) == 0)
    {
      $found = true;
      $tmp   = $old_order_by[$i];
      
      for ($j = $i; $j > 0; --$j)
        $old_order_by[$j] = $old_order_by[$j - 1];
      
      $old_order_by[0] = $tmp;
      
      break;
    }
  }
  
  if (!$found)
  {
    for ($i = count($old_order_by); $i > 0; --$i)
      $old_order_by[$i] = $old_order_by[$i - 1];
    
    $old_order_by[0]['col']   = $new_col;
    $old_order_by[0]['order'] = 'ASC';
  }
  
  return $old_order_by;
}

/**** end util stuff; begin the browsing ****/

function browse_stuff($data, $sql_link)
{
  $what         = $data['what'];
  $id_filters   = array
                  (
                    'cat'    => get_id_from_query('cat_id',    $data),
                    'artist' => get_id_from_query('artist_id', $data),
                    'album'  => get_id_from_query('album_id',  $data),
                    'genre'  => get_id_from_query('genre_id',  $data)
                  );
  $name_filters = array
                  (
                    'song'   => validate_name_from_data($data['song_name']  ),
                    'artist' => validate_name_from_data($data['artist_name']),
                    'album'  => validate_name_from_data($data['album_name'] ),
                    'genre'  => validate_name_from_data($data['genre_name'] )
                  );
  
  // if a particular id filter is set, it should take priority over the name filter, and the name filter should be ignored.
  foreach($name_filters as $name => $value)
    if (isset($id_filters[$name]) && $id_filters[$name] != null)
      $name_filters[$name] = null;
  
  // not filters
  $order_by = $data['order_by'];
  $offset   = $data['offset'];
  $count    = $data['count'];
  
  if (!isset($offset) || !is_numeric($offset))
    $offset = 0;
  else
    $offset = intval($offset);
  
  if (!isset($count) || !is_numeric($count))
    $count = 40;
  else
    $count = intval($count);
  
  if (isset($what))
  {
    if (strcmp($what, "songs") == 0)
      browse_songs    ($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link);
    else if (strcmp($what, "artists") == 0)
      browse_artists  ($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link);
    else if (strcmp($what, "albums") == 0)
      browse_albums   ($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link);
    else if (strcmp($what, "genres") == 0)
      browse_genres   ($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link);
    else if (strcmp($what, "playlists") == 0)
      browse_playlists($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link);
    else if (strcmp($what, "catalogs") == 0)
      browse_catalogs($data, $sql_link);
    else
      browse_everything($sql_link);
  }
}

function browse_songs($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link)
{
  // should never be searching for a null song name.  (the song name shouldn't be null.)
  if (strcmp($name_filters['song'], '') == 0)
    $name_filters['song'] = null;
  
  $sql_params = array();
  $order_by   = validate_order_by($order_by, $col_dict);
  $col_dict   = array
                (
                  'song'       => 'song_title', 'track'        => 'track', 'artist'      => 'artist_name', 'album'      => 'album_name', 'genre' => 'genre_name',
                  'song_title' => 'song_title', 'track_number' => 'track', 'artist_name' => 'artist_name', 'album_name' => 'album_name'
                );
  if (count($order_by) == 0)
  {
    $order_by = array
                (
                  0 => array('col' => 'album_name', 'order' => 'ASC'),
                  1 => array('col' => 'track',      'order' => 'ASC'),
                  2 => array('col' => 'song_title', 'order' => 'ASC')
                );
  }
  $order_by_str = get_order_by_string($order_by);
  
  $join_type    = 'LEFT';
  if ($id_filters['artist'] !== null || ($name_filters['artist'] !== null && strlen($name_filters['artist']) > 0))
    $join_type  = 'INNER';
  
  // $query_end should be called $from.  i'll rename it later.  maybe.
  $query_end    = "FROM songs AS s\n" .
                  '  ' . $join_type . " JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
                  '  ' . $join_type . " JOIN artists AS ar ON ar.id = s_ar.artist_id\n" .
                  '  ' . $join_type . " JOIN songs_artists AS s_ar2 ON s_ar2.song_id = s.id\n" .
                  '  ' . $join_type . " JOIN artists AS ar2 ON ar2.id = s_ar2.artist_id\n";
  if ($id_filters['artist'] !== null)
  {
    $query_end .= '    AND ar2.id IN (' . $id_filters['artist'] . ")\n";
  }
  else if ($name_filters['artist'] != null && strlen($name_filters['artist']) > 0)
  {
    $query_end .= "    AND ar2.name LIKE \"%:artist_name_filter%\"\n";
    $sql_params[':artist_name_filter'];
  }
  
  $join_type    = 'LEFT';
  if ($id_filters['album'] !== null || ($name_filters['album'] !== null && strlen($name_filters['album']) > 0))
    $join_type  = 'INNER';
  
  $query_end   .= '  ' . $join_type . " JOIN songs_albums AS al_s ON al_s.song_id = s.id\n" .
                  '  ' . $join_type . " JOIN albums AS al ON al.id = al_s.album_id\n";
  
  if ($id_filters['album'] !== null)
  {
    $query_end .= '    AND al.id IN (' . $id_filters['album'] . ")\n";
  }
  else if ($name_filters['album'] !== null && strlen($name_filters['album']) > 0)
  {
    $query_end .= "    AND al.name LIKE \"%:album_name_filter%\"\n";
    $sql_params[':album_name_filter'] = $name_filters['album'];
  }
  
  $join_type    = 'LEFT';
  if ($id_filters['genre'] !== null || ($name_filters['genre'] !== null && strlen($name_filters['genre']) > 0))
    $join_type  = 'INNER';
  
  $query_end .= '  ' . $join_type . ' JOIN songs_genres AS s_g ON s_g.song_id = s.id';
  $query_end .= '  ' . $join_type . ' JOIN genres AS g ON g.id = s_g.genre_id';
  
  if ($id_filters['genre'] !== null)
  {
    $query_end .= "\n    AND g.id IN (" . $id_filters['genre'] . ')';
  }
  else if ($name_filters['genre'] !== null && strlen($name_filters['genre']) > 0)
  {
    $query_end .= "\n    AND g.name LIKE \"%:genre_name_filter%\"";
    $sql_params[':genre_name_filter'] = $name_filters['genre'];
  }
  
  $has_where = false;
  
  if ($id_filters['cat'] !== null || (isset($name_filters['song']) && $name_filters['song'] !== null))
  {
    $has_where  = true;
    $query_end .= "\nWHERE ";
    
    if ($id_filters['cat'] !== null)
      $query_end .= "s.catalog_id=$cat_id";
    
    if ($id_filters['cat'] !== null && isset($name_filters['song']) && $name_filters['song'] !== null)
      $query_end .= ' AND ';
    
    if (isset($name_filters['song']) && $name_filters['song'] !== null)
    {
      $query_end .= 's.name LIKE "%:song_name_filter%"';
      $sql_params[':song_name_filter'] = $name_filters['song'];
    }
  }
  
  if ($id_filters['artist'] === null && $name_filters['artist'] !== null && strlen($name_filters['artist']) === 0)
  {
    $where .= ($has_where ? '  AND' : 'WHERE') . " s_ar.artist_id IS NULL\n";
    $has_where = true;
  }
  
  if ($id_filters['album'] === null && $name_filters['album'] !== null && strlen($name_filters['album']) === 0)
  {
    $where .= ($has_where ? '  AND' : 'WHERE') . " al_s.album_id IS NULL\n";
    $has_where = true;
  }
  
  if ($id_filters['genre'] === null && $name_filters['genre'] !== null && strlen($name_filters['genre']) === 0)
  {
    $where .= ($has_where ? '  AND' : 'WHERE') . " s.genre_id IS NULL\n";
    $has_where = true;
  }
  
  $query    = "SELECT COUNT(DISTINCT s.id) AS ttl_count\n" .
              $query_end . "\n" .
              $where;
  
  $result   = $sql_link->query($query);
  if ($result === false)
  {
    echo 'this query died:<br />';
    $query = str_replace("\n", "<br />\n", $query);
    $query = str_replace(' ',  '&nbsp;',   $query);
    echo $query . "<br />\n";
    echo "with this error: <br />\n";
    echo $sql_link->errorInfo()[2];
    return;
  }
  
  $tmp       = $result->fetch(PDO::FETCH_ASSOC);
  $ttl_count = intval($tmp['ttl_count']);
  
  // just checkin'.  (never trust user data.  it's not actually that much of a problem if offset is too big ('cause then the query just returns 0 rows), but it's still better to check.)
  if ($offset > $ttl_count)
    $offset = 0;
  
  $artist_group = 'DISTINCT \'<a href="#" onclick="' /* "> */ . 'filter_by(\\\'artist\\\', \', ar.id, \', \\\'id\\\'); return false;">\', ar.name, \'</a>\', s_ar.conjunction ORDER BY s_ar.list_order';
  
  $query     = 'SELECT s.id AS song_id, s.name AS song_title, ar.id AS artist_id, GROUP_CONCAT(' . $artist_group . ' SEPARATOR "") AS artist_name, al.id AS album_id, al.name AS album_name, al_s.track_number AS track, g.id AS genre_id, g.name AS genre_name' . "\n" .
               $query_end . "\n" .
               $where .
               "GROUP BY s.id\n" .
               'ORDER BY ' . $order_by_str . "\n" .
               'LIMIT ' . $offset . ', ' . $count . ';';
  
  $queue_html       = '<a href="#" class="toxic_yellow" onclick="' . // ">
                      'var feedback = exec_cmd(\'now_playing\', \'queue_song\', \'id=%song_id%\', true, function(feedback) { } ); ' .
                      'if (feedback.length > 0) alert(\'could not queue %title%:\n\' + feedback);' .
                      'load_view(\'now_playing\', \'now_playing\', \'\', document.getElementById(\'now_playing_div\'), function() {}, true, true); ' .
                      'return false;">&nbsp;+&nbsp;</a>';
  $download         = '<a href="download.php?id=%song_id%" class="toxic_yellow" target="tab">dl</a>';
  
//$artist_td  = '<a href="#" onclick="filter_by(\'artist\', %artist_id%, \'id\'); return false;">%artist_name%</a>';
  $artist_td  = '%artist_name%';
  $album_td   = '<a href="#" onclick="filter_by(\'album\',  %album_id%,  \'id\'); return false;">%album_name%</a>';
  $genre_td   = '<a href="#" onclick="filter_by(\'genre\',  %genre_id%,  \'id\'); return false;">%genre_name%</a>';
  
  $columns    = array
                (
                  0 => array('html' => null,            'post' => null,          'th' => 'q',  'td' => $queue_html   ),
                  1 => array('html' => 'title',         'post' => 'song_title',  'th' => null, 'td' => '%song_title%'),
                  2 => array('html' => 'artist',        'post' => 'artist_name', 'th' => null, 'td' => $artist_td    ),
                  3 => array('html' => 'album',         'post' => 'album_name',  'th' => null, 'td' => $album_td     ),
                  4 => array('html' => '&nbsp;#&nbsp;', 'post' => 'track',       'th' => null, 'td' => '%track%',    ),
                  5 => array('html' => 'genre',         'post' => 'genre_name',  'th' => null, 'td' => $genre_td     ),
                  6 => array('html' => null,            'post' => null,          'th' => '',   'td' => $download     )
                );
  
  list_stuff($data, $query, 'songs', $id_filters, $name_filters, $columns, $order_by, $offset, $count, $ttl_count, $sql_params, $sql_link);
}

function browse_artists($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link)
{
  if ($name_filters['artist'] !== null && strlen($name_filters['artist']) == 0)
    $name_fitlers['artist'] = null;
  
  $sql_params = array();
  $col_dict   = array('artist' => 'artist_name', 'artist_name' => 'artist_name');
  $order_by   = validate_order_by($order_by, $col_dict);
  
  $order_by_str = 'ASC';
  if (count($order_by) == 1)
    $order_by_str = $order_by[0]['order'];
  else
    $order_by = array(0 => array('col' => 'artist_name', 'order' => 'ASC'));
  
  //// begin query_end ////
  // $query_end should be called $from.  i'll rename it later.  maybe.
  $query_end = "FROM artists AS ar\n" .
               "  INNER JOIN songs_artists AS s_ar ON s_ar.artist_id=ar.id\n" .
               "  INNER JOIN songs s ON s.id = s_ar.song_id\n";
  
  if ($id_filters['song'] !== null)
  {
    $query_end .= '    AND s.id IN (' . $id_filters['song'] . ")\n";
  }
  else if ($name_filters['song'] !== null && strlen($name_filters['song']) > 0)
  {
    $query_end .= "    AND s.name LIKE \"%:song_name_filter%\"\n";
    $sql_params[':song_name_filter'] = $name_filters['song'];
  }
  
  if ($id_filters['cat'] != null)
    $query_end .= '    AND s.catalog_id=' . $id_filters['cat'] . "\n";
  
  if (isset($id_filters['album']) && $id_filters['album'] !== null)
  {
    $query_end .= "  INNER JOIN songs_albums AS s_al ON s_al.song_id = s.id\n" .
                  '    AND s_al.album_id IN (' . $id_filters['album'] . ")\n";
  }
  else if (isset($name_filters['album']) && $name_filters['album'] !== null)
  {
    if (strlen($name_filters) == 0)
    {
      $query_end .= "  LEFT JOIN songs_albums AS s_al ON s_al.song_id = s.id\n";
    }
    else
    {
      $query_end .= "  INNER JOIN songs_albums AS s_al ON s_al.song_id = s.id\n" .
                    "  INNER JOIN albums       AS al   ON al.id        = s_al.album_id\n" .
                    "    AND al.name LIKE \"%:album_name_filter%\"\n";
      $sql_params[':album_name_filter'] = $name_filters['album'];
    }
  }
  
  $join_type = ($id_filters['genre'] !== null || ($name_filters['genre'] !== null && strlen($name_filters['genre']) > 0) ? 'INNER' : 'LEFT');
  $query_end .= '  ' . $join_type . " JOIN songs_genres AS s_g ON s_g.song_id = s.id\n";
  $query_end .= '  ' . $join_type . " JOIN genres AS g ON g.id = s_g.genre_id\n";
  if ($id_filters['genre'] !== null)
  {
    $query_end .= '    AND g.id IN (' . $id_filters['genre'] . ")\n";
  }
  else if ($name_filters['genre'] !== null && strlen($name_filters['genre']) > 0)
  {
    $query_end .= "    AND g.name LIKE \"%:genre_name_filter%\"\n";
    $sql_params[':genre_name_filter'] = $name_filters['genre'];
  }
  
  //// end query_end ////
  
  $first_where = true;
  
  // skipping songs; i should never have an artist w/o songs.
  
  if ($id_filters['album'] === null && $name_filters['album'] !== null && strlen($name_filters['album']) === 0)
  {
    $where .= ($first_where ? 'WHERE' : '  AND') . " s_al.album_id IS NULL\n";
    $first_where = false;
  }
  
  // note: not allowing the user to filter the artist list by artists that don't exist.
  if (isset($name_filters['artist']) && $name_filters['artist'] !== null && strlen($name_filters['artist']) > 0)
  {
    $where .= ($first_where ? 'WHERE' : '  AND') . ' ar.name LIKE "%' . $name_filters['artist'] . "%\"\n";
    $first_where = false;
  }
  
  if ($id_filters['genre'] === null && $name_filters['genre'] !== null && strlen($name_filters['genre']) === 0)
  {
    $where .= ($first_where ? 'WHERE' : '  AND') . " s.genre_id IS NULL\n";
    $first_where = false;
  }
  
  $query  = "SELECT COUNT(DISTINCT(ar.id)) AS num_artists\n" . $query_end . "\n" . $where;
  
  $result = $sql_link->query($query);
  if ($result === false)
  {
    echo "this query failed:<br />\n";
    $query = str_replace("\n", "<br />\n", $query);
    $query = str_replace(' ',  '&nbsp;',   $query);
    echo $query . "<br />\n";
    echo "with this error:<br />\n";
    echo $sql_link->errorInfo()[2];
    return;
  }
  
  $result    = $result->fetch(PDO::FETCH_ASSOC);
  $ttl_count = intval($result['num_artists']);
  
  // just checkin'.  (never trust user data.  it's not actually that much of a problem if offset is too big ('cause then the query just returns 0 rows), but it's still better to check.)
  if ($offset > $ttl_count)
    $offset = 0;
  
  $query     = "SELECT ar.id AS artist_id, ar.name AS artist_name, COUNT(DISTINCT(s_ar.song_id)) AS num_songs, GROUP_CONCAT(DISTINCT g.name SEPARATOR ', ') AS genre_names\n" .
               $query_end . "\n" .
               $where .
               "GROUP BY ar.id\n" .
               'ORDER BY ar.name ' . $order_by_str . "\n" .
               'LIMIT ' . $offset . ', ' . $count;
  
  $queue_html       = '<a href="#" class="toxic_yellow" onclick="alert(\'TO DO: queue up everything by %artist_name%.\'); return false;">&nbsp;+&nbsp;</a>';
  
  $artist_td        = '<a href="#" onclick="filter_by(\'artist\', %artist_id%, \'id\'); return false;">' . '%artist_name%</a>';
  $genre_td         = $filter_lnk_start . '%genre_id%</a>';
  
  $columns          = array
                      (
                        0 => array('html' => null,         'clickable' => false, 'post' => null,          'th' => 'q',  'td' => $queue_html    ),
                        1 => array('html' => 'artist',     'clickable' => true,  'post' => 'artist_name', 'th' => null, 'td' => $artist_td     ),
                        2 => array('html' => '# of songs', 'clickable' => false, 'post' => null,          'th' => null, 'td' => '%num_songs%'  ),
                        3 => array('html' => 'genres',     'clickable' => false, 'post' => null,          'th' => null, 'td' => '%genre_names%')
                      );
  
  list_stuff($data, $query, 'artists', $id_filters, $name_filters, $columns, $order_by, $offset, $count, $ttl_count, $sql_params, $sql_link);
}

function browse_albums($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link)
{
  $sql_params = array();
  $col_dict   = array
                (
                  'album_name' => 'album_name', 'artist_name' => 'artist_name', 'num_songs'  => 'num_tracks', 'year' => 'year',
                  'album'      => 'album_name', 'artist'      => 'artist_name', 'num_tracks' => 'num_tracks'
                );
  
  $order_by   = validate_order_by($order_by, $col_dict);
  
  if (count($order_by) == 0)
    $order_by = array
                (
                  0 => array('col' => 'album_name', 'order' => 'ASC'),
                  1 => array('col' => 'artists',    'order' => 'ASC'),
                  2 => array('col' => 'num_tracks', 'order' => 'ASC')
                );
  
  $order_by_str = get_order_by_string($order_by);
  
  // $query_end should be called $from.  i'll rename it later.  maybe.
  $query_end    = "FROM albums AS al\n" .
                  "  INNER JOIN songs_albums AS s_al ON s_al.album_id = al.id\n" .
                  "  INNER JOIN songs        AS s    ON s.id = s_al.song_id\n";
  if (isset($id_filters['song']) && $id_filters['song'] !== null)
  {
    $query_end .= '    AND s.id IN (' . $id_filters['song'] . ")\n";
  }
  else if (isset($name_filters['song']) && $name_filters['song'] !== null)
  {
    $query_end .= "    AND s.name LIKE \"%:song_name_filter%\"\n";
    $sql_params[':song_name_filter'] = $name_filters['song'];
  }
  
  $has_id_filter    = (isset($id_filters['artist'])    && $id_filters['artist']   !== null);
  $has_name_filter  = (isset($name_filters['aritist']) && $name_filters['artist'] !== null && strlen($name_filters['artist']) != 0);
  
  $artist_join_type = ($has_id_filter || $has_name_filter ? 'INNER' : 'LEFT');
  $query_end   .= '  ' . $artist_join_type . " JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
                  '  ' . $artist_join_type . " JOIN artists       AS ar   ON ar.id = s_ar.artist_id\n";
  
  if ($has_id_filter)
  {
    $query_end .= '    AND ar.id IN (' . $id_filters['artist'] . ")\n";
  }
  else if ($has_name_filter)
  {
    $query_end .= "    AND ar.name LIKE \"%:artist_name_filter%\"\n";
    $sql_params[':artist_name_filter'] = $name_filters['artist'];
  }
  
  $has_id_filter   = (isset($id_filters['genre'])   && $id_filters['genre']   !== null);
  $has_name_filter = (isset($name_filters['genre']) && $name_filters['genre'] !== null && strlen($name_filters['genre']) > 0);
  $genre_join_type = ($has_id_filter || $has_name_filter ? 'INNER' : 'LEFT');
  
  $query_end   .= "  $genre_join_type JOIN songs_genres AS s_g ON s_g.song_id = s.id\n";
  $query_end   .= "  $genre_join_type JOIN genres AS g ON g.id = s_g.genre_id\n";
  if ($has_id_filter)
  {
    $query_end .= '    AND g.id IN (' . $id_filters['genre'] . ")\n";
  }
  else if ($has_name_filter)
  {
    $query_end .= "    AND g.name LIKE \"%:genre_name_filter%\"\n";
    $sql_params[':genre_name_filter'] = $name_filters['genre'];
  }
  
  $first_where  = true;
  $where        = '';
  if (isset($name_filters['album']) && $name_filters['album'] !== null && strlen($name_filters['album']) > 0)
  {
    $where     .= ($first_where ? 'WHERE ' : '  AND') . ' al.name LIKE "%' . $name_filters['album'] . "%\"\n";
    $first_where = false;
  }
  
  if (isset($name_filters['artist']) && $name_filters['artist'] !== null && strlen($name_filters['artist']) == 0)
  {
    $where     .= ($first_where ? 'WHERE ' : '  AND') . " s_ar.artist_id IS NULL\n";
    $first_where = false;
  }
  
  if (isset($name_filters['genre']) && $name_filters['genre'] !== null && strlen($name_filters['genre']) == 0)
  {
    $where     .= ($first_where ? 'WHERE ' : '  AND') . " s.genre_id IS NULL\n";
    $first_where = false;
  }
  
  $query        = "SELECT COUNT(DISTINCT(al.id)) AS num_albums\n" . $query_end . $where;
  
  $result       = $sql_link->query($query);
  if ($result === false)
  {
    echo "this query failed:<br />\n";
    $query = str_replace("\n", "<br />\n", $query);
    $query = str_replace(' ',  '&nbsp;',   $query);
    echo $query . "<br />\n";
    echo "with this error:<br />\n";
    echo $sql_link->errorInfo()[2];
    return;
  }
  $tmp        = $result->fetch(PDO::FETCH_ASSOC);
  $ttl_count  = $tmp['num_albums'];
  
  // just checkin'.  (never trust user data.  it's not actually that much of a problem if offset is too big ('cause then the query just returns 0 rows), but it's still better to check.)
  if ($offset > $ttl_count)
    $offset = 0;
  
  $query      = 'SELECT DISTINCT al.id AS album_id, al.name AS album_name, COUNT(DISTINCT s.id) AS num_tracks, GROUP_CONCAT(DISTINCT ar.name SEPARATOR ", ") AS artists, GROUP_CONCAT(DISTINCT g.name SEPARATOR ", ") AS genres' . "\n" .
                $query_end .
                $where .
                "GROUP BY al.id\n" .
                'ORDER BY ' . $order_by_str . "\n" .
                'LIMIT ' . $offset . ', ' . $count . ';';
  
  $queue_html = '<a href="#" class="toxic_yellow" onclick="' . // ">
                'var feedback = exec_cmd(\'now_playing\', \'queue_album\', \'id=%album_id%\', true, function(feedback) { } ); ' .
                'if (feedback.length > 0) alert(\'could not queue %album_name%:\n\' + feedback);' .
                'load_view(\'now_playing\', \'now_playing\', \'\', document.getElementById(\'now_playing_div\'), function() {}, true, true); ' .
                'return false;' .
                '">&nbsp;+&nbsp;</a>';
  $album_td   = '<a href="#" onclick="filter_by(\'album\', %album_id%, \'id\'); return false;">' . '%album_name%</a>';
  
  $columns    = array
                (
                  0 => array('html' => null,         'clickable' => false, 'post' => null,         'th' => 'q',  'td' => $queue_html   ),
                  1 => array('html' => 'album',      'clickable' => true,  'post' => 'album_name', 'th' => null, 'td' => $album_td     ),
                  2 => array('html' => '# of songs', 'clickable' => true,  'post' => 'num_tracks', 'th' => null, 'td' => '%num_tracks%'),
                  3 => array('html' => 'artist(s)',  'clickable' => false, 'post' => null,         'th' => null, 'td' => '%artists%'   ),
                  4 => array('html' => 'genre(s)',   'clickable' => false, 'post' => null,         'th' => null, 'td' => '%genres%'    )
                );
  
  list_stuff($data, $query, 'albums', $id_filters, $name_filters, $columns, $order_by, $offset, $count, $ttl_count, $sql_params, $sql_link);
}

function browse_genres($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link)
{
  $col_dict     = array('genre_name' => 'genre_name');
  $order_by     = validate_order_by($order_by, $col_dict);
  $order_by_str = 'ASC';
  $sql_params   = array();
  
  if (count($order_by) == 1)
    $order_by_str = $order_by[0]['order'];
  else
    $order_by     = array(0 => array('col' => 'genre_name', 'order' => 'ASC'));
  
  // $query_end should be called $from.  i'll rename it later.  maybe.
  $query_end = "FROM genres AS g\n" .
               "  INNER JOIN songs_genres AS s_g ON s_g.genre_id = g.id\n";
               "  INNER JOIN songs AS s ON s.id = s_g.song_id\n";
  
  if (isset($id_filters['song']) && $id_filters['song'] !== null)
  {
    $query_end .= '    AND s.id = ' . $id_filters['song'] . "\n";
  }
  else if (isset($name_filters['song']) && $name_filters['song'] !== null && strlen($name_filters['song']) > 0)
  {
    $query_end .= "    AND s.name LIKE \"%:song_name_filter%\"\n";
    $sql_params[':song_name_filter'] = $name_filters['song'];
  }
  
  if (isset($id_filters['artist']) && $id_filters['artist'] !== null)
  {
    $query_end .= "  INNER JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
                  '    AND s_ar.artist_id IN (' . $id_filters['artist'] . ")\n";
  }
  else if (isset($name_filters['artist']) && $name_filters['artist'] !== null && strlen($name_filters['artist']) > 0)
  {
    $query_end .= "  INNER JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
                  "  INNER JOIN artists AS ar ON ar.id = s_ar.artist_id\n" .
                  "    AND ar.name LIKE \"%:artist_name_filter%\"\n";
    $sql_params[':artist_name_filter'] = $name_filters['artist'];
  }
  
  if (isset($id_filters['album']) && $id_filters['album'] !== null)
  {
    $query_end .= "  INNER JOIN songs_albums AS s_al ON s_al.song_id = s.id\n" .
                  '    AND s_al.album_id IN (' . $id_filters['album'] . ")\n";
  }
  else if (isset($name_filters['album']) && $name_filters['album'] !== null && strlen($name_filters['album']) > 0)
  {
    $query_end .= "  INNER JOIN songs_albums AS s_al ON s_al.song_id = s.id\n" .
                  "  INNER JOIN albums AS al ON al.id = s_al.album_id\n" .
                  "    AND al.name LIKE \"%:album_name_filter%\"\n";
    $sql_params[':album_name_filter'] = $name_filters['album'];
  }
  
  $first_where  = true;
  $where        = '';
  
  if (isset($name_filters['genre']) && $name_filters['genre'] !== null && strlen($name_fiters['genre']) > 0)
  {
    $query .= ($first_where ? 'WHERE' : '  AND') . " g.name LIKE \"%:genre_name_filter%\"\n";
    $sql_params[':genre_name_filter'] = $name_filters['genre'];
    $first_where = false;
  }
  
  if (isset($name_filters['artist']) && $name_filters['artist'] !== null && strlen($name_filters['artist']) == 0)
  {
    $query .= ($first_where ? 'WHERE' : '  AND') . " s_ar.artist_id IS NULL\n";
    $first_where = false;
  }
  
  if (isset($name_filters['album']) && $name_filters['album'] !== null && strlen($name_filters['album']) == 0)
  {
    $query .= ($first_where ? 'WHERE' : '  AND') . " s_al.artist_id IS NULL\n";
    $first_where = false;
  }
  
  $query  = "SELECT COUNT(DISTINCT g.id) AS num_genres\n" .
            $query_end;
  
  $result = $sql_link->query($query);
  if ($result === false)
  {
    echo "this query failed:<br />\n";
    $query = str_replace("\n", "<br />\n", $query);
    $query = str_replace(' ',  '&nbsp;',   $query);
    echo $query . "<br />\n";
    echo "with this error:<br />\n";
    echo $sql_link->errorInfo()[2];
    return;
  }
  $tmp        = $result->fetch(PDO::FETCH_ASSOC);
  $ttl_count  = $tmp['num_genres'];
  
  // just checkin'.  (never trust user data.  it's not actually that much of a problem if offset is too big ('cause then the query just returns 0 rows), but it's still better to check.)
  if ($offset > $ttl_count)
    $offset = 0;
  
  $query  = "SELECT g.id AS genre_id, g.name AS genre_name, COUNT(DISTINCT s.id) AS num_songs\n" .
            $query_end;
  
  if (isset($name_filters['genre']) && $name_filters['genre'] != null)
    $query .= 'WHERE g.name LIKE "%' . $name_filters['genre'] . "%\"\n";
  
  $query .= "GROUP BY g.id\n" .
            'ORDER BY genre_name ' . $order_by_str . "\n" .
            'LIMIT ' . $offset . ', ' . $count . ';';
  
  $genre_td   = '<a href="#" onclick="filter_by(\'genre\', %genre_id%, \'id\'); return false;">' . '%genre_name%</a>';
  
  $columns    = array
                (
                  0 => array('html' => 'genre',      'clickable' => true,  'post' => 'genre_name', 'th' => null, 'td' => $genre_td),
                  1 => array('html' => '# of songs', 'clickable' => false, 'post' => null,         'th' => null, 'td' => '%num_songs%')
                );
  
  list_stuff($data, $query, 'genres', $id_filters, $name_filters, $columns, $order_by, $offset, $count, $ttl_count, $sql_params, $sql_link);
}

function browse_playlists($data, $id_filters, $name_filters, $order_by, $offset, $count, $sql_link)
{
  echo 'TO DO';
}

function browse_catalogs($data, $sql_link)
{

}

function browse_everything($sql_link)
{
?>
<div id="browse_artists_div">
  <a href="#" id="show_hide_artists_lnk" class="show_hide" onclick="show_hide_browse_lists('artists'); return false;">+artists</a><br />
  <div id="browse_artists_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
</div>
<div id="browse_albums_div">
  <a href="#" id="show_hide_albums_lnk" class="show_hide" onclick="show_hide_browse_lists('albums'); return false;">+albums</a><br />
  <div id="browse_albums_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
</div>
<div id="browse_genres_div">
  <a href="#" id="show_hide_genres_lnk" class="show_hide" onclick="show_hide_browse_lists('genres'); return false;">+genres</a><br />
  <div id="browse_genres_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
</div>
<!---
<div id="browse_playlists_div">
  <a href="#" id="show_hide_playlists_lnk" class="show_hide" onclick="show_hide_browse_lists('playlists'); return false;">+playlists</a><br />
  <div id="browse_playlists_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
</div>
--->
<div id="browse_songs_div">
  <a href="#" id="show_hide_songs_lnk" class="show_hide" onclick="show_hide_browse_lists('songs'); return false;">+songs</a><br />
  <div id="browse_songs_list_div" style="display: none;"></div>
</div>
<?php //>
}

// ok 1 more util function
function get_offset_link($new_offset, $new_count, $what, $txt)
{
  $lnk = '<a href="#" class="toxic_brown" onclick="' . // >
           'var view_node = document.getElementById(\'browsing_' . $what . '_get_my_parent\').parentNode; ' .
           'var old_params_div = document.getElementById(\'browsing_' . $what . '_get_my_parent\'); ' .
           'if (old_params_div == null) ' .
           '{ ' .
             'alert(\'request data not available for ' . $what . '\'); ' .
             'return false; ' .
           '} ' .
           'var new_params = old_params_div.innerHTML; ' .
           'new_params = new_params.replace(/&amp;amp;/g, \'&\'); ' .
           'new_params = set_query_param_value(new_params, \'offset\', ' . $new_offset . ', true); ' .
           'new_params = set_query_param_value(new_params, \'count\', '  . $new_count  . ', true); ' .
           'load_view(\'browse\', \'browse\', new_params, view_node, function() {}, true); ' .
           'return false;' .
         '"> ' . $txt . ' </a>';
  
  return $lnk;
}

function list_stuff($data, $query, $what, $id_filters, $name_filters, $columns, $order_by, $offset, $count, $ttl_count, $sql_params, $sql_link)
{
  $fbq         = $query; // fbq == feedback query
  
  $sql_stmt    = $sql_link->prepare($query);
  $sql_results = $sql_stmt->execute($sql_params);
  if ($sql_results === false)
  {
    $html_query = str_replace(' ',  '&nbsp;',   $query);
    $html_query = str_replace("\n", "<br />\n", $html_query);
    
?>
this query died:<br />
<br />
<?=$html_query?><br />
<br />
with this error: <?=$sql_link->errorInfo()[2]?><br />
<?php // >
    
    return;
  }
  
  // for printing out the current order things are listed in the table in
  $pretty_order_by_str = get_pretty_order_by_string($order_by);
  
  // for listing and getting rid of a filter
  $filter_links = '';
  
  foreach ($id_filters as $filter_name => $val)
  {
    if ($val == null || strlen($val) == 0)
      continue;
    
    // filter name
    $filter_link = (str_replace('_', '&nbsp;', $filter_name) . ' is one of (');
    
    // filter value
    $query       = 'SELECT name FROM ' . $filter_name . 's WHERE id IN (' . $val . ') ORDER BY id ASC;';
    $result      = $sql_link->query($query);
    if ($result === false)
    {
      echo 'query "' . $query . '" died:<br />' . $sql_link->errorInfo()[2];
      continue;
    }
    
    $ids = explode(',', $val);
    for ($i = 0; $i < $result->rowCount(); ++$i)
    {
      $tmp          = $ids; // need to make a copy, so we can change the copy
      array_splice($tmp, $i, 1);
      $ids_str      = implode(',', $tmp);
      
      $this_name    = $result->fetch(PDO::FETCH_ASSOC);
      $filter_link .= $this_name[$sql_col];
      
      if ($result->rowCount() > 1)
        $filter_link .= ' [<a href="#" onclick="' . // ">
                          'var util_div   = document.getElementById(\'browsing_' . $what . '_get_my_parent\'); ' .
                          'var view_div   = util_div.parentNode; ' .
                          'var new_params = util_div.innerHTML; ' .
                          'new_params     = new_params.replace(/&amp;amp;/g, \'&\'); ' .
                          'new_params     = remove_query_param(new_params, \'page\'); ' .
                          'new_params     = remove_query_param(new_params, \'view\'); ' .
                          'new_params     = remove_query_param(new_params, \'skip_login_check\'); ' .
                          'new_params     = set_query_param_value(new_params, \'' . $filter_name . '_id\', &quot;' . $ids_str . '&quot;, true); ' .
                          'load_view(\'browse\', \'browse\', new_params, view_div, function() {}, true);' .
                          'return false;' .
                        '">&nbsp;x&nbsp;</a>]';
      
      $filter_link .= ', ';
    }
    
    $filter_link   = substr($filter_link, 0, strlen($filter_link) - 2) . ') [';
    
    // link to remove filter
    $filter_link  .= '<a href="#" onclick="' . // ">
                       'var util_div   = document.getElementById(\'browsing_' . $what . '_get_my_parent\'); ' .
                       'var view_div   = util_div.parentNode; ' .
                       'var new_params = util_div.innerHTML; ' .
                       'new_params     = new_params.replace(/&amp;amp;/g, \'&\'); ' .
                       'new_params     = remove_query_param(new_params, \'page\'); ' .
                       'new_params     = remove_query_param(new_params, \'view\'); ' .
                       'new_params     = remove_query_param(new_params, \'skip_login_check\'); ' .
                       'new_params     = remove_query_param(new_params, \'' . $filter_name . '_id\'); ' .
                       'load_view(\'browse\', \'browse\', new_params, view_div, function() {}, true);' .
                       'return false;' .
                     '">&nbsp;x&nbsp;</a>]';
    
    $filter_links .= $filter_link . "<br />\n";
  }
  
  foreach ($name_filters as $filter_name => $val)
  {
    if ($val === null)
      continue;
    
    $filter_link = (str_replace('_', '&nbsp;', $filter_name) . ' is ' . (strlen($val) === 0 ? 'null' : 'like "' . $val . '"'));
    
    // link to remove filter
    $filter_link  .= ' [<a href="#" onclick="' . // >
                       'var util_div   = document.getElementById(\'browsing_' . $what . '_get_my_parent\'); ' .
                       'var view_div   = util_div.parentNode; ' .
                       'var new_params = util_div.innerHTML; ' .
                       'new_params     = new_params.replace(/&amp;amp;/g, \'&\'); ' .
                       'new_params     = remove_query_param(new_params, \'page\'); ' .
                       'new_params     = remove_query_param(new_params, \'view\'); ' .
                       'new_params     = remove_query_param(new_params, \'skip_login_check\'); ' .
                       'new_params     = remove_query_param(new_params, \'' . $filter_name . '_name\'); ' .
                       'load_view(\'browse\', \'browse\', new_params, view_div, function() {}, true);' .
                       'return false;' .
                     '">&nbsp;x&nbsp;</a>]';
    
    $filter_links .= $filter_link . "<br />\n";
  }
  
  if (strlen($filter_links) > 0)
    $filter_links = "<div class=\"toxic_green\" style=\"display: inline;\">filters:</div><br />\n" . $filter_links;
  
  // for moving to the previous page of results
  $prev_page = '&nbsp;&lt;&nbsp;';
  if ($offset > 0)
  {
    $new_offset = $offset - $count;
    if ($new_offset < 0)
      $new_offset = 0;
    
    $prev_page = get_offset_link($new_offset, $count, $what, $prev_page);
  }
  
  // for moving to the next page of results
  $next_page = '&nbsp;&gt;&nbsp;';
  if ($offset + $count < $ttl_count)
    $next_page = get_offset_link($offset + $count, $count, $what, $next_page);
?>
<div id="browsing_<?=$what?>_get_my_parent" style="display: none;"><?=get_post_query($data)?></div>
<div class="toxic_green" style="display: inline;">metametadata:</div><br />
<div class="toxic_green" style="display: inline;">current sort order:</div> <?=$pretty_order_by_str?><br />
<div class="toxic_green" style="display: inline;">showing results</div> <?=($ttl_count > 0 ? ($offset + 1) : 0)?> - <?=(($ttl_count < $offset + $count) ? $ttl_count : $offset + $count)?> of <?=$ttl_count?><br />
<?=$filter_links?>
<br />
<?php // >
  
  if ($ttl_count == 0)
  {
    echo 'found no results.<br />';
  }
  else
  {
?>
<table>
  <tr>
    <th class="edge_case" style="padding-left: 10px; padding-right: 10px;">
      <?=($prev_page . "\n")?>
    </th>
<?php // >
    for ($c = 0; $c < count($columns); ++$c)
    {
      
      $th = '';
      if ($columns[$c]['html'] != null)
      {
        if ($columns[$c]['post'] != null)
        {
          $th_order_by     = get_new_order_by($columns[$c]['post'], $order_by);
          $th_order_by_str = get_order_by_string($th_order_by);
          $th_order_by_str = str_replace(' ', '%20', $th_order_by_str);
          
          $th .= '<a href="#" class="toxic_brown" onclick="var old_params = document.getElementById(\'browsing_' . $what . '_get_my_parent\').innerHTML; ' . // >
                                                          'var new_params = old_params.replace(/&amp;amp;/g, \'&\'); ' .
                                                          'new_params = set_query_param_value(new_params, \'order_by\', \'' . $th_order_by_str . '\'); ' .
                                                          'load_view(\'browse\', ' .
                                                                    '\'browse\', ' .
                                                                    'new_params, ' .
                                                                    'document.getElementById(\'browsing_' . $what . '_get_my_parent\').parentNode, ' .
                                                                    'function () {}, ' .
                                                                    'true); return false;">';
        }
        
        $th .= $columns[$c]['html'];
        
        if ($columns[$c]['post'] != null)
          $th .= '</a>';
      }
      else
      {
        $th = $columns[$c]['th'];
      }
?>
    <th style="padding-left: 10px; padding-right: 10px;">
      <?=($th . "\n")?>
    </th>
<?php // >
  }
?>
    <th>
      <?=($next_page . "\n")?>
    </th>
  </tr>
<?php // >
    
    for ($r = 0; $r < $sql_results->rowCount(); ++$r)
    {
?>
  <tr>
    <td id="td_select_<?=$r?>" class="edge_case" style="text-align: right">
      <?=(($r == 0 ? '|' : '&nbsp;') . "\n")?>
    </td>
<?php // >
      $row = $sql_results->fetch(PDO::FETCH_ASSOC);
      for ($c = 0; $c < count($columns); ++$c)
      {
        echo '    <td class="'/*>*/ . (($r % 2 == 0 && $c % 2 == 1) || ($r % 2 == 1 && $c % 2 == 0) ? 'high' : 'low') . "light\" style=\"padding-left: 10px; padding-right: 10px;\">\n";
        echo '      ';
        
        $col_out = $columns[$c]['td'];
        preg_match_all('/%[A-Za-z_]+%/', $col_out, $matches);
        
        for ($i = 0; $i < count($matches[0]); ++$i)
        {
          $sql_match = substr($matches[0][$i], 1, strlen($matches[0][$i]) - 2);
          $col_out   = str_replace($matches[0][$i], $row[$sql_match], $col_out);
        }
        
        echo $col_out . "\n";
        echo "    </td>\n";
      }
?>
    <td class="edge_case">
      &nbsp;
    </td>
  </tr>
<?php // >
    }
    
    echo '</table>';
  }
  
//  $fbq = str_replace(' ',  '&nbsp;',   $fbq);
//  $fbq = str_replace("\n", "<br />\n", $fbq);
//  echo $fbq;
}

browse_stuff($_POST, $sql_link);
?>