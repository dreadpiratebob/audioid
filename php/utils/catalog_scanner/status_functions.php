<?php

function add_status($new_status, $session_id, $dump_to_screen = true)
{
  session_start($session_id);
  
  if (!array_key_exists('scan_log', $_SESSION))
  {
    $_SESSION['scan_log'] = array();
  }
  
  if (!array_key_exists('scan_status', $_SESSION))
  {
    $_SESSION['scan_status'] = array();
  }
  
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

function write_log()
{
  if (!isset($_SESSION['scan_status']) || !is_array($_SESSION['scan_status']) || count($_SESSION['scan_status']) == 0)
    return 'got no log to write.';
  
  $name       = $_SESSION['scan_status']['name'];
  $start_time = $_SESSION['scan_status']['start_time'];
  $log        = 'catalog "' . $name . '" scanned from ' . $_SERVER['REMOTE_ADDR'] . '; started at ' . $start_time . ".\n";
  for ($i = 0; $i < count($_SESSION['scan_log']); $i++)
  {
    $line = $_SESSION['scan_log'][$i] . "\n";
    $line = preg_replace("/[^\n-þ]/", '?', $line);
    $log .= $line;
  }
  
  $result = file_put_contents("/web/log/scans/{$name} {$start_time}.log", $log);
  if ($result === false)
  {
    $_SESSION['scan_status'][count($_SESSION['scan_status'])] = 'failed to write log.';
    return 'failed to write log.';
  }
  
  return 'wrote the log.';
}

?>