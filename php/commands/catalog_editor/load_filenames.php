<?php // >

function start($data, $sql_link, $session_id)
{
  $cat_id     = $data['id'];
  $separators = $data['separators'];
  
  if (!isset($cat_id) || !is_numeric($cat_id))
  {
    add_status('data error (error code 30)', $session_id);
    add_status('done.', $session_id);
    return 'data error (error code 30)';
  }
  
  if (!isset($separators))
  {
    add_status('data error (error code 31)', $session_id);
    add_status('done.', $session_id);
    return 'data error (error code 31)';
  }
  
  if (strlen($separators) > 0 && preg_match_all('/^[a-zA-Z0-9\.&_\(\) %,]+(\|[a-zA-Z0-9\.&_\(\) %,]+)*$/', $separators, $matches) != 1)
  {
    add_status('data error (error code 32)', $session_id);
    add_status('done.', $session_id);
    return 'invalid separators.  (you gave "' . $separators . '".)';
  }
  
  $query       = 'SELECT id, name, base_path FROM catalogs WHERE id=' . $cat_id . ';';
  $sql_catalog = $sql_link->query($query);
  if ($sql_catalog === false)
  {
    add_status('query "' . $query . '" died:<br />' . $sql_link->error . '<br />done.', $session_id);
    return -4;
  }
  
  if ($sql_catalog->num_rows != 1)
  {
    add_status('error: found ' . $sql_catalog->num_rows . ' catalogs.');
    return -5;
  }
  
  $sql_catalog = $sql_catalog->fetch_array(MYSQLI_ASSOC);
  $cat_name    = $sql_catalog['name'];
  
  session_start($session_id);
  if (isset($_SESSION['cat' . $cat_id . 'mp3s']))
    unset($_SESSION['cat' . $cat_id . 'mp3s']);
  
  $_SESSION['scan_status']['name'] = $cat_name;
  session_write_close();
  
  add_status('got separators "' . $separators . '"', $session_id);
  
  $base_dir = $sql_catalog['base_path'];
  scan_directory($base_dir, $cat_id, $cat_name, $sql_link, $session_id);
  
  add_status('',      $session_id);
  
  session_start($session_id);
  
  $separators = str_replace('%27', '&', $separators);
  
  $_SESSION['cat_scanner']['id']         = $cat_id;
  $_SESSION['cat_scanner']['index']      = 0;
  $_SESSION['cat_scanner']['separators'] = explode('|', $separators);
  
  return $cat_id;
}

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
    
    session_start($session_id);
    $_SESSION['cat_scanner']['file_list'][$_SESSION['cat_scanner']['file_cnt']] = $full_fn;
    $_SESSION['cat_scanner']['file_cnt']++;
    session_write_close();
    
    add_status($status . 'it\'s an mp3; adding it to the list...', $session_id);
    
    // parse_mp3($cat_id, $full_fn, $sql_link, $session_id);
  }
}

function add_status($new_status, $session_id)
{
  session_start($session_id);
  $_SESSION['scan_status'][count($_SESSION['scan_status'])] = $new_status;
  session_write_close();
}

session_start();
$_SESSION['cat_scanner']['file_cnt']   = 0;
$_SESSION['cat_scanner']['file_list']  = array();
$_SESSION['scan_status']['start_time'] = date('Y-m-d H:i:s.u');
$session_id = session_id();
session_write_close();

set_time_limit(0);

$feedback .= start($data, $sql_link, $session_id);

?>