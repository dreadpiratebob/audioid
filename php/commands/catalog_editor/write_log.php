<?php

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
  
  $result = file_put_contents('/var/log/my_music/scans/' . $name . ' ' . $start_time . '.log', $log);
  if ($result === false)
  {
    $_SESSION['scan_status'][count($_SESSION['scan_status'])] = 'failed to write log.';
    return 'failed to write log.';
  }
  
  return 'wrote the log.';
}

$feedback .= write_log();

?>