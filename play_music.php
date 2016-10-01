<?php

session_start();

$current = null;
$next    = null;

if (count($_SESSION['now_playing']['song_list']) > 0)
{
  $current = $_SESSION['now_playing']['current'];
  if (!isset($current) || $current == null || !is_numeric($current))
  {
    $_SESSION['now_playing']['current'] = 0;
    $current = 0;
  }
  
  $next = $current + 1;
  if ($next > count($_SESSION['now_playing']['song_list']))
    $next = null;
}

$song1 = ($current === null ? null   : $_SESSION['now_playing']['song_list'][$current]);
if (!isset($song1['artist']))
  $song1['artist'] = null;

$song2 = ($next    === null ? $song1 : $_SESSION['now_playing']['song_list'][$next]);
if (!isset($song2['artist']))
  $song2['artist'] = null;

?><!DOCTYPE html>
<html>
  <head>
    <title>
      <?=($song1['title'] . ($song1['artist'] == null ? '' : ' by ' . $song1['artist']) . " [playing]\n")?>
    </title>
    <script type="text/javascript" src="js/ajax.js"></script>
    <script type="text/javascript" src="js/music_player.js"></script>
    <link   type="text/css"        rel="stylesheet" href="css.css" />
  </head>
  <body onload="load_page(<?=($song1 == null ? 'null' : $song1['id'])?>, <?=($song2 == null ? 'false' : 'true')?>);">
<?php
if ($song1 == null)
{
  echo "    didn't find any songs to play.\n";
}
else
{
?>
    <audio controls id="audio_1" onended="skip_to_next(2);" onplay="on_play(1);" onpause="on_pause(1);" autoplay oncanplaythrough="document.getElementById('audio_1').autoplay = false; document.getElementById('audio_1').oncanplaythrough = function(event) {};">
      <source id="audio_src_1" src="embed.php?id=<?=$song1['id']?>" type="audio/mpeg" />
      your browse doesn't support &lt;audio&gt; tags.
    </audio>
    <audio controls id="audio_2" onended="skip_to_next(1);" onplay="on_play(2);" onpause="on_pause(2);">
      <source id="audio_src_2" src="embed.php?id=<?=$song2['id']?>" type="audio/mpeg" />
      your browse doesn't support &lt;audio&gt; tags.
    </audio>
<?php
}
?>
    <div id="dbg"></div>
    <div id="check_list" style="display: none"><?=$song1['id']?>/<?=$song2['id']?></div>
  </body>
</html>