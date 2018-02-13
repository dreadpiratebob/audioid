<?php //>

function delete_catalog($data, $sql_link)
{
  $cat_id = $data['cat_id'];
  $fb = '';
  
  if (!isset($cat_id) || !is_numeric($cat_id))
    return 'data error (error code 36)<br />';
  
  $cat_id = intval($cat_id);
  $query  = "call delete_catalog({$cat_id});"; // i'm trusting PHP's 'intval' function here to clean out any bad data and to make MySQL's cleaning unnecessary.
  $result = $sql_link->query($query);
  if ($result === false)
    die('query "' . $query . '" died: ' . $sql_link->errorInfo()[2]);
  
  return 'successfully deleted the catalog.';
}

if (isset($_POST) && is_array($_POST) && count($_POST) > 0)
  $feedback .= delete_catalog($_POST, $sql_link);
else if (isset($_GET) && is_array($_GET) && count($_GET) > 0)
  $feedback .= delete_catalog($_GET, $sql_link);

?>