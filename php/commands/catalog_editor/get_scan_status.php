<?php //>

$max = $data['max'];
if (isset($max) && is_numeric($max))
{
  $max   = intval($max);
  $start = count($_SESSION['scan_status']) - $max;
  
  for ($i = ($start < 0 ? 0 : $start); $i < count($_SESSION['scan_status']); ++$i)
  {
    $status = $_SESSION['scan_status'][$i] . "\n";
    $status = str_replace(' ', '&nbsp;', $status);
    $status = str_replace("\n", "<br />\n", $status);
    echo $status;
  }
}
else
{
  echo 'data error (error code 3)';
}

?>