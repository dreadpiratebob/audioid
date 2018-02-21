<?php // >

function update_catalog($data, $sql_link)
{
  /** data validation & cleanup **/
  $fb   = '';
  $id   = $data['cat_id'];
  $name = $data['name'];
  $path = $data['path'];
  
  if (!isset($id) || !is_numeric($id))
    $fb .= "data error (error code 35)<br />\n";
  
  $id = intval($id);
  
  if (preg_match('/^[A-Za-z0-9 _]+$/', $name) !== 1)
    $fb .= "invalid name; names can only contain alphanumeric characters, spaces and underscores.<br />\n";
  
  if (preg_match('/^[A-Za-z0-9\/ _]+$/', $path) !== 1)
    $fb .= "invalid path; paths can only contain alphanumeric characters, spaces, underscores and slashes.<br />\n";
  
  if (strlen($fb) > 0)
    return $fb;
  
  /** end data validation & cleanup **/
  
  $query  = "SELECT update_catalog({$id}, :name, :path) AS update_result;";
  $update = $sql_link->prepare($query);
  $temp   = $update->execute(array(':name' => $name, ':path' => $path));
  
  if ($temp === false)
    return "query \"{$query}\" died:<br />\n{$update->errorInfo()[2]}";
  
  $arr_update = $update->fetch(PDO::FETCH_ASSOC);
  
  if ($arr_update['update_result'] === 0)
    return "the path that was supplied is invalid; either a catalog exists with a base path that's a subdirectory of the supplied path, or a catalog exists with a base path that the supplied path is a subdirectory of.<br />\n";
  
  return "done.<br />\n";
}

$dat = 'nope';
if (isset($_POST) && is_array($_POST) && count($_POST) > 0)
  $dat = $_POST;
else if (isset($_GET) && is_array($_GET) && count($_GET) > 0)
  $dat = $_GET;

if (is_array($data))
  $feedback .= update_catalog($dat, $sql_link);
?>