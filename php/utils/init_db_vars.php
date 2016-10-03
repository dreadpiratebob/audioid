<?php // >

// make sure this stays sorted alphabetically.
$auto_admin_commands = array('add', 'delete', 'load_mp3', 'scan', 'update');

if (!isset($db_username) || (strcmp($db_username, 'audioid') != 0 && strcmp($db_username, 'audioid_admin') != 0))
{
  $found = false;
  if (isset($cmd))
  {
    // don't like this, but i dislike it less than passing a username / password through an ajax request.
    $min   = 0;
    $max   = count($auto_admin_commands) - 1;
    
    while ($min <= $max && !$found)
    {
      $cur = intval(($min + $max)/2);
      $cmp = strcmp($cmd, $auto_admin_commands[$cur]);
      
      if ($cmp == 0)
        $found = true;
      else if ($cmp > 0)
        $min = $cur + 1;
      else // if ($cmp < 0)
        $max = $cur - 1;
    }
  }
  
  if ($found)
  {
    $db_username = 'audioid_admin';
    $db_password = '_you_are_chickenfeed_nub_';
  }
  else
  {
    $db_username = 'audioid';
    $db_password = 'useless_password';
  }
}

if (!isset($db_password))
  $db_password = '';

?>