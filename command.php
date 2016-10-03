<?
// this & view.php don't go through index.php.  that's because they're gateways to the commands called by the js and the views loaded by the js (respectively) that allow me to hide
// the fs architecture. (why do i wanna hide the fs architecture? well... i feel like things are more secure this way, and i feel like it'll be a lot harder for someone to copy me.
// unless, of course, i let them.)

function run_cmd($data)
{
  // i don't really need both of these, but it mirrors the $cmd architecture in place in index.php and adds a little security
  $cmd  = $data['cmd'];
  $page = $data['page'];
  
  if (!isset($page) || !isset($cmd))
  {
    //include("php/index.php"); // 404 :)
    return "O.O";
  }
  
  $fn = 'php/commands/' . $page . '/' . $cmd . '.php';
  
  if (!file_exists($fn))
    return "!";
  
  $php_root    = 'php/';
  
  include_once('php/utils/init_db_vars.php');
  
  if (!isset($db_username))
    $db_username = $data['db_username'];
  
  if (isset($db_username) && strcmp($db_username, 'audioid_admin') == 0)
  {
    $db_password = '_you_are_chickenfeed_nub_';
  }
  else
  {
    $db_username = 'audioid';
    $db_password = '_music_now_';
  }
  
  include_once('php/utils/startup_connections.php');
  $data['sql_link'] = $sql_link;
  
  include_once($fn);
  
  $sql_link->close();
  
  return $feedback;
}

if (count($_POST) > 0)
  echo run_cmd($_POST);
else if (count($_GET) > 0)
  echo run_cmd($_GET);
else
  echo "";