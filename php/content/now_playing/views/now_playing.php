<?php

$blank_txt = '';
$play_lnk  = '';

if (array_key_exists('now_playing', $_SESSION) && count($_SESSION['now_playing']['song_list']) > 0)
{
  $blank_txt   = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
  $play_lnk    = '&nbsp;' .
                 '<a href="play_music.php" class="toxic_green" target="tab" ' . // >
                   'onmouseover="document.getElementById(\'now_playing_hints_div\').innerHTML=\'play&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\';" ' .
                   'onmouseout="document.getElementById(\'now_playing_hints_div\').innerHTML=\'' . $blank_txt . '\'" ' .
//                   'onclick="load_play_window(); return false;"' .
                 '>&gt;</a>' .
                 '&nbsp;' .
                 '<a href="#" class="toxic_green" ' . // >
                   'onmouseover="document.getElementById(\'now_playing_hints_div\').innerHTML=\'clear the list\';" ' .
                   'onmouseout="document.getElementById(\'now_playing_hints_div\').innerHTML=\'' . $blank_txt . '\'" ' .
                   'onclick="' .
                     'exec_cmd(\'now_playing\', \'kill_list\', \'count=' . time() . '\', true); ' .
                     'load_view(\'now_playing\', \'now_playing\', \'\', document.getElementById(\'now_playing_song_list_div\').parentNode, function () {}, true); ' .
                     'return false;"' .
                 '>x</a>' .
                 '&nbsp;';
  
  // $has_prev = (isset($_SESSION['now_playing']['current']) && $_SESSION['now_playing']['current'] !== null && $_SESSION['now_playing']['current'] > 0);
  $has_next_prev_link = (count($_SESSION['now_playing']['song_list']) > 0);
  if ($has_next_prev_link)
    $play_lnk .= '<a href="#" class="toxic_green" ' . // >
                   'onmouseover="document.getElementById(\'now_playing_hints_div\').innerHTML=\'previous song&nbsp;\';" ' .
                   'onmouseout="document.getElementById(\'now_playing_hints_div\').innerHTML=\'' . $blank_txt . '\'" ' .
                   'onclick="' . // >
                     'exec_cmd(\'now_playing\', \'decrement_current_song\', \'to=' . count($_SESSION['now_playing']['song_list']) . '\', true); ' .
                     'load_view(\'now_playing\', \'now_playing\', \'\', document.getElementById(\'now_playing_song_list_div\').parentNode, function() {}, true, true); ' .
                     'return false;"' .
                 '>';
  $play_lnk   .= '&lt;&lt;';
  if ($has_next_prev_link)
    $play_lnk .= '</a>';
  
  $play_lnk   .= '&nbsp;';
  
  // $has_next = (isset($_SESSION['now_playing']['current']) && $_SESSION['now_playing']['current'] !== null && $_SESSION['now_playing']['current'] < count($_SESSION['now_playing']['song_list']) - 1);
  if ($has_next_prev_link)
    $play_lnk .= '<a href="#" class="toxic_green" ' . // >
                   'onmouseover="document.getElementById(\'now_playing_hints_div\').innerHTML=\'next song&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\';" ' .
                   'onmouseout="document.getElementById(\'now_playing_hints_div\').innerHTML=\'' . $blank_txt . '\'" ' .
                   'onclick="' . // >
                     'exec_cmd(\'now_playing\', \'increment_current_song\', \'to=' . count($_SESSION['now_playing']['song_list']) . '\', true); ' .
                     'load_view(\'now_playing\', \'now_playing\', \'\', document.getElementById(\'now_playing_song_list_div\').parentNode, function() {}, true, true); ' .
                     'return false;"' .
                 '>';
  $play_lnk   .= '&gt;&gt;';
  if ($has_next_prev_link)
    $play_lnk .= '</a>';
  
  $play_lnk   .= '&nbsp;';
}

?>queued songs:<?=($play_lnk)?><div id="now_playing_hints_div"><?=$blank_txt?></div>
<div id="now_playing_song_list_div"></div>