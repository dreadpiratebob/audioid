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
  
  $query        = 'SELECT base_path FROM catalogs;';
  $sql_catalogs = $sql_link->query($query);
  
  if ($sql_catalogs === false)
    return $fb . 'query "' . $query . '" died: <br />' . $sql_link->$sql_link->errorInfo()[2];
  
  $catalogs = $sql_catalogs->fetchAll(PDO::FETCH_ASSOC);
  for ($i = 0; $i < count($catalogs); ++$i)
  {
    $catalog  = $catalogs[$i];
    $cat_path = $catalog['base_path'];
    
    $fn1      = (strlen($path) <  strlen($cat_path) ? $path : $cat_path);
    $fn2      = (strlen($path) >= strlen($cat_path) ? $path : $cat_path);
    
    $fn2      = substr($fn2, 0, strlen($fn1));
    
    if (strcmp($fn1, $fn2) == 0)
      return $fb . 'invalid path; either a catalog already exists in a subfolder of your path or a catalog already exists in a superfolder of your path.<br />';
  }
  
  /** end data validation & cleanup **/
  
  $query  = 'INSERT INTO catalogs (name, base_path) VALUES("' . $name . '", "' . $path . '");';
  $result = $sql_link->query($query);
  
  if ($result === false)
    return $fb . 'query "' . $query . '" died:<br />' . "\n" . $sql_link->$sql_link->errorInfo()[2];
  else
    return $fb;
}

if (isset($_POST) && is_array($_POST) && count($_POST) > 0)
  $feedback .= add_catalog($_POST, $sql_link);
else if (isset($_GET) && is_array($_GET) && count($_GET) > 0)
  $feedback .= add_catalog($_GET, $sql_link);

?>