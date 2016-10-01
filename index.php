<?php
header("Content-Type: text/html; charset=utf-8");

include_once('php/utils/init_vars.php');
include_once('php/utils/startup_connections.php');

if (isset($cmd_fn))
{
  include_once($cmd_fn);
}

?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>
      <?=((isset($title) && strlen($title) > 0) ? ($title . " - ") : (''))?>audioid music player
    </title>
    <link rel="stylesheet" type="text/css" href="css.css" />
    <script type="text/javascript" src="js/ajax.js"></script>
    <script type="text/javascript" src="js/now_playing.js"></script>
    <script type="text/javascript" src="js/util.js"></script>
  </head>
  <body onload="load_index(event)" onkeydown="add_keystroke(event);">
    <div class="topnav">
      <div class="topsearch">
        <form name="search_frm" id="search_frm" action="search.php" method="POST" onsubmit="var search_txt = document.getElementById('search_txt'); search_txt.value = search_txt.value.replace(/&/g, '%26');/*document.getElementById('search_frm').submit();*/">
          <input  type="text"   id="search_txt" name="search_txt" size="40" />
          <button type="button" id="search_button">search</button>
        </form>
      </div>
      audioid music player: <?=($topnav_txt . "\n")?>
    </div>
    <div class="leftnav">
<?php include('php/content/leftnav.php'); echo "\n"; ?>
    </div>
    <div id="wrapper">
      <div id="now_playing_div"></div>
      <div id="content">
<?php include('php/content/' . $page . '.php'); echo "\n"; ?>
      </div>
      <div id="feedback"><?=$feedback?></div>
    </div>
    <div id="footer">
      all web (non-music) content copyright &copy; 2014 <a href="http://heinrich.hoza.us" target="tab">heinrich hoza</a>
    </div>
  </body>
</html><?php

$sql_link->close();

?>