<?php

function add_status($new_status, $session_id, $dump_to_screen = true)
{
  session_start($session_id);
  
  $lines = explode('\n', $new_status);
  
  for ($i = 0; $i < count($lines); ++$i)
  {
    $_SESSION['scan_log'][count($_SESSION['scan_log'])] = $lines[$i];
    if ($dump_to_screen)
      $_SESSION['scan_status'][count($_SESSION['scan_status'])] = $lines[$i];
  }
  
  session_write_close();
}

function dump_query($title, $query, $params, $session_id, $dump_to_screen = false)
{
  $deparamed_query = $query;
  foreach ($params as $param => $value)
    $deparamed_query = str_replace($param, "\"{$value}\"", $deparamed_query);
  
  $log_message = "\n\n----query dump: {$title} ----\nquery w/ params:\n{$query}\n\nquery w/o params:\n{$deparamed_query}\n\nparams:\n" . print_r($params, true) . "----end query dump: {$title} ----\n\n";
  add_status($log_message, $session_id, $dump_to_screen);
}

?>