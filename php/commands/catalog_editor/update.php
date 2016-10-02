<?php // >

function update_catalog($data, $sql_link)
{
  /** data validation & cleanup **/
  $id   = $data['cat_id'];
  $name = $data['name'];
  $path = $data['path'];
  
  if (!isset($id) || !is_numeric($id))
    $fb .= 'data error (error code 35)<br />';
  
  $id = intval($id);
  
  if (preg_match('/^[A-Za-z0-9 _]+$/', $name) !== 1)
    $fb .= 'invalid name; names can only contain alphanumeric characters, spaces and underscores.<br />' . "\n";
  
  if (preg_match('/^[A-Za-z0-9\/ _]+$/', $path) !== 1)
    $fb .= 'invalid path; paths can only contain alphanumeric characters, spaces, underscores and slashes.<br />' . "\n";
  
  if (strlen($fb) > 0)
    return $fb;
  
  $query        = "SELECT base_path FROM catalogs WHERE id!=$id;";
  $sql_catalogs = $sql_link->query($query);
  
  if ($sql_catalogs === false)
    return $fb . 'query "' . $query . '" died: <br />' . $sql_link->errorInfo()[2];
  
  for ($i = 0; $i < $sql_catalogs->rowCount(); ++$i)
  {
    $catalog  = $sql_catalogs->fetch_array();
    $cat_path = $catalog['base_path'];
    
    $fn1          = (strlen($path) <  strlen($cat_path) ? $path : $cat_path);
    $fn2          = (strlen($path) >= strlen($cat_path) ? $path : $cat_path);
    
    $fn2          = substr($fn2, 0, strlen($fn1));
    
    if (strcmp($fn1, $fn2) == 0)
      return $fb . 'invalid path; either a catalog already exists in a subfolder of your path or a catalog already exists in a superfolder of your path.<br />';
  }
  
  /** end data validation & cleanup **/
  
  $query  = "UPDATE catalogs SET name=:name, base_path=:path WHERE id=$id;";
  $temp   = $sql_link->prepare($query);
  $result = $temp->execute(array(':name' => $name, ':path' => $path));
  
  if ($result === false)
    return $fb . 'query "' . $query . '" died:<br />' . "\n" . $sql_link->errorInfo()[2];
  else
    return $fb . "done.<br />\n";
}

$dat = 'nope';
if (isset($_POST) && is_array($_POST) && count($_POST) > 0)
  $dat = $_POST;
else if (isset($_GET) && is_array($_GET) && count($_GET) > 0)
  $dat = $_GET;

if (is_array($data))
  $feedback .= update_catalog($dat, $sql_link);
?>