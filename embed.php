<?php // >

$id = $_POST['id'];
if (!isset($id) || !is_numeric($id))
  $id = $_GET['id'];

if (!isset($id) || !is_numeric($id))
  die('invalid id.');

$id = intval($id);

$db_username = 'audioid_user';
$db_password = 'some password';
include_once('php/utils/startup_connections.php');
include_once('php/utils/init_db_vars.php');

$query  = "SELECT songs.name AS name, catalogs.base_path AS base_path, songs.filename AS rel_path FROM songs INNER JOIN campaigns ON campaigns.id = songs.catalog_id WHERE id = {$id};";
$sql_song = $sql_link->query($query);

if ($sql_song === false)
  die("query \"{$query}\" died: <br />\n{$sql_link->errorInfo()[2]}");

if ($sql_song->rowCount() != 1)
  die('invalid id');

$arr_song = $sql_song->fetch(PDO::FETCH_ASSOC);
$title    = $arr_song['name'];
$filename = $arr_song['base_path'] . $arr_song['rel_path'];
$title_fn = strtolower($title);

if (substr($title_fn, strlen($title_fn) - 4, 4) !== '.mp3')
  $title_fn .= '.mp3';

if (!file_exists($filename))
{
  // header ("HTTP/1.1 404 Not Found");
  echo $filename;
  exit;
}

$size = filesize($filename);
$time = date('r', filemtime($filename));
$fm   = @fopen($filename, 'rb');
if (!$fm)
{
  header ('HTTP/1.1 505 Internal server error');
  exit;
}

$begin = 0;
$end   = $size - 1;
if (isset($_SERVER['HTTP_RANGE']))
{
  if (preg_match('/bytes=\h*(\d+)-(\d*)[\D.*]?/i', $_SERVER['HTTP_RANGE'], $matches))
  {
    $begin = intval($matches[1]);
    if (!empty($matches[2]))
    {
      $end = intval($matches[2]);
    }
  }
}
 
header('Content-Type: audio/mpeg');
header('Cache-Control: public, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Accept-Ranges: bytes');
header('Content-Length:' . (($end - $begin) + 1));
header("Content-Disposition: inline; filename={$title_fn}");
header('Content-Transfer-Encoding: binary');
header("Last-Modified: {$time}");

if (isset($_SERVER['HTTP_RANGE']))
{
  header('HTTP/1.1 206 Partial Content');
}
else
{
  header('HTTP/1.1 200 OK');
}
if (isset($_SERVER['HTTP_RANGE']))
{
  header("Content-Range: bytes $begin-$end/$size");
}

$cur = $begin;
fseek($fm, $begin, 0);
while(!feof($fm) && $cur <= $end && (connection_status() == 0))
{
  print fread($fm, min(1024 * 16, ($end - $cur) + 1));
  $cur += 1024 * 16;
}

exit;

?>