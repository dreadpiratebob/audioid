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

$query  = 'SELECT name, filename FROM songs WHERE id=' . $id . ';';
$result = $sql_link->query($query);

if ($result === false)
  die('query "' . $query . '" died: <br />' . $sql_link->errorInfo()[2]);

if ($result->num_rows != 1)
  die('invalid id');

$tmp      = $result->fetch(PDO:FETCH_ASSOC);
$title    = $tmp['name'];
$filename = $tmp['filename'];

header('Content-Disposition: attachment; filename="' . strtolower($title) . '.mp3"');
header('Content-Length: ' . filesize($filename));
header('Content-Transfer-Encoding: binary');
header('Content-Type: audio/mpeg');
header('Expires: 0');

ob_clean();
readfile($filename);
exit;

?>