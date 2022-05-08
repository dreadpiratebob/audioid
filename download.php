<?php // >

$id = $_POST['id'];
if (!isset($id) || !is_numeric($id))
  $id = $_GET['id'];

if (!isset($id) || !is_numeric($id))
  die('invalid id.');

$id = intval($id);

$db_username = 'audioid';
$db_password = 'useless_password';
include_once('php/utils/startup_connections.php');

$query    = "SELECT songs.name AS name, catalogs.base_path AS base_path, songs.filename AS rel_path FROM songs INNER JOIN catalogs ON catalogs.id = songs.catalog_id WHERE songs.id = {$id};";
$sql_song = $sql_link->query($query);

if ($sql_song === false)
  die("query \"{$query}\" died: <br />\n{$sql_link->errorInfo()[2]}");

if ($sql_song->rowCount() != 1)
  die('invalid id.');

$arr_song = $sql_song->fetch(PDO::FETCH_ASSOC);
$filename = $arr_song['base_path'] . $arr_song['rel_path'];

header('Content-Disposition: attachment; filename="' . strtolower($arr_song['name']) . '.mp3"');
header('Content-Length: ' . filesize($filename));
header('Content-Transfer-Encoding: binary');
header('Content-Type: audio/mpeg');
header('Expires: 0');

ob_clean();
readfile($filename);
exit;

?>