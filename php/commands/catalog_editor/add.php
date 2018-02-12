<?php //>

function add_catalog($data, $sql_link)
{
  /** data validation & cleanup **/
  $name = $data['name'];
  $path = $data['path'];
  $fb   = '';
  
  if (preg_match('/^[A-Za-z0-9 _]+$/', $name) !== 1)
    $fb .= 'invalid name; names can only contain alphanumeric characters, spaces and underscores.<br />' . "\n";
  
  if (preg_match('/^[A-Za-z0-9\/ _]+$/', $path) !== 1)
    $fb .= 'invalid path; paths can only contain alphanumeric characters, spaces, underscores and slashes.<br />' . "\n";
  
  if (strlen($fb) > 0)
    return $fb;
  
  $query    = "SELECT catalog_path_is_used('{$path}') as is_used;";
  $sql_path = $sql_link->query($query);
  $arr_path = $sql_path->fetch(PDO::FETCH_ALL);
  
  if ($arr_path['is_used'] === 1)
    return 'invalid path; either a catalog already exists in a subfolder of your path or a catalog already exists in a superfolder of your path.<br />';
  /** end data validation & cleanup **/
  
  $query  = 'CALL insert_catalog(:name, :path);';
  $stmt   = $sql_link->prepare($query);
  $result = $stmt->execute(array(':name' => $name, ':path' => $path);
  
  if ($result === false)
    return "query '{$query}' died:<br />\n{$sql_link->$sql_link->errorInfo()[2]}";
  else
    return '';
}

if (isset($_POST) && is_array($_POST) && count($_POST) > 0)
  $feedback .= add_catalog($_POST, $sql_link);
else if (isset($_GET) && is_array($_GET) && count($_GET) > 0)
  $feedback .= add_catalog($_GET, $sql_link);

?>