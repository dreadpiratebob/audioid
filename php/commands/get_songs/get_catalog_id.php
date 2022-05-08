<?php

function get_catalog_id($data)
{
  if (!isset($data))
  {
    http_response_code(400);
    echo 'no data found.  please provide either a catalog_name or a base_path.';
    return;
  }
  
  $sql_params = array();
  $query      = 'SELECT id FROM catalogs WHERE ';
  
  $key = 'catalog_name';
  if (array_contains_key($key, $data))
  {
    $query .= "name=:{$key}";
    $sql_params[$key] = $data[$key];
  }
  
  $key = 'base_path';
  if (array_contains_key($key, $data))
  {
    if (count($sql_params) > 0)
    {
      $query .= " AND ";
    }
    $query .= "name=:{$key}";
    $sql_params[$key] = $data[$key];
  }
  
  if (count($sql_params) == 0)
  {
    http_response_code(400);
    echo 'no useful data found.  please provide either a catalog_name or a base_path.';
    return;
  }
  
  $stmt    = $sql_link->prepare($query);
  $sql_ids = $stmt->execute($sql_params);
  
  if ($stmt === false)
  {
    http_response_code(500);
    echo "query died.<br />\n<br />\nquery:<br />\n{$query}<br />\n<br />\nerror:<br />\n{$sql_link->errorInfo()[2]}";
    return;
  }
  
  if ($sql_ids->numRows() === 0)
  {
    http_response_code(404);
    echo 'no catalogs found.';
    return;
  }
}

get_catalog_id($_GET);

?>