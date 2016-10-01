<?php
function get_view($data)
{
  $page = $data['page'];
  $view = $data['view'];
  
  if (!isset($page) || !isset($view))
    return 'x';
  
  $view = str_replace('.', '/', $view);
  
  $fn = 'php/content/' . $page . '/views/' . $view . '.php';
  if (!file_exists($fn))
    return 'unk (error code 37)';
  
  include_once('php/utils/init_db_vars.php');
  include_once('php/utils/startup_connections.php');
  
  /****************** view ***********************/
  ob_start();
  
  // get the view
  include($fn);
  $html = ob_get_contents();
  
  // make sure all the appropriate chars are escaped
  $html = str_replace("\\",   "\\\\", $html);
  $html = str_replace("\"",   "\\\"", $html);
  $html = str_replace("\r\n", "\n",   $html);
  $html = str_replace("\r",   "\n",   $html);
  $html = str_replace("\n",   "\\n",  $html);
  
//  $html .= "page: " . $page . " / view: " . $view;
  ob_end_clean();
  /**************** end view **********************/
  
  ob_start();
  
  $on_load_fn = 'php/content/' . $page . '/on_load/' . $view . '.php';
  if (file_exists($on_load_fn))
  {
    include($on_load_fn);
    $on_load = ob_get_contents();
    /* if i (we?) decide to conform to the standards on json.org, uncomment this
    $on_load = str_replace("\"",   "\\\"", $on_load);
    $on_load = str_replace("\r\n", "\n",   $on_load);
    $on_load = str_replace("\r",   "\n",   $on_load);
    $on_load = str_replace("\n",   "\\n",  $on_load);
    */
  }
  else
  {
    $on_load = '    ';
  }
  
  ob_end_clean();
  
  $view_content =
  "{\n" .
  "  \"view\": \"" . $html . "\",\n" .
  
  /* if i (we?) decide to conform to the standards on json.org, add a slash at the beginning of this line.
  
  "  \"on_load\": \"function()\\n" .
  "  {\\n" .
  $on_load . "\\n" .
  "  }\"\n" .
  
  /*/ // old way
  
  "  \"on_load\": function()\n" .
  "  {\n" .
  $on_load . "\n" .
  "  }\n" .
    
  //*/
  '}';
  
  if (isset($sql_link))
    $sql_link->close();
  
  return $view_content;
}

header('Content-Type: application/json');

$_data = false;

if (isset($_SESSION['user_id']))
{
  if (count($_POST) > 0)
    $_data = $_POST;
  else if (count($_GET) > 0)
    $_data = $_GET;
}
else
{
  if (count($_POST) > 0 && isset($_POST['skip_login_check']) && strcmp($_POST['skip_login_check'], "true") == 0)
    $_data = $_POST;
  else if (count($_GET) > 0 && isset($_GET['skip_login_check']) && strcmp($_GET['skip_login_check'], "true") == 0)
    $_data = $_GET;
}

if ($_data === false)
  echo '{ }';
else
  echo get_view($_data);
?>