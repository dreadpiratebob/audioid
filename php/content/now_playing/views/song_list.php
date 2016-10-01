<?php // >

function get_bump_js($index, $id, $dir)
{
  $js = 'var fb = exec_cmd(\'now_playing\', \'bump_song\', \'index=' . $index . '&id=' . $id . '&dir=' . $dir . '\', true, function(feedback) {if (feedback.length > 0) alert(feedback);}); ' .
  //      'if (fb.length > 0) ' .
  //        'alert(\'slow down.  this takes a sec sometimes.\'); ' .
        'load_view(\'now_playing\', \'song_list\', \'refresh=false\', document.getElementById(\'song_list_table\').parentNode, function() {}, true, true); ';
  
  return $js;
}

if (!isset($_SESSION['now_playing']) || !is_array($_SESSION['now_playing']) || !isset($_SESSION['now_playing']['song_list']) || !is_array($_SESSION['now_playing']['song_list']) || count($_SESSION['now_playing']['song_list']) == 0)
{
  echo 'none';
}
else
{
  $cur_song_num    = $_SESSION['now_playing']['current'];
  $refresh_song_js = "load_view('now_playing', 'song_list', '', document.getElementById('now_playing_song_list_div'), function() {}, true); ";
?>
<table id="song_list_table">
<?php // >
  for ($i = 0; $i < count($_SESSION['now_playing']['song_list']); ++$i)
  {
    $is_playing = (isset($cur_song_num) && $i === $cur_song_num);
    $song       = $_SESSION['now_playing']['song_list'][$i];
    
    echo '  <tr' . ($is_playing ? ' class="toxic_blue"' : '') . ">\n";
    
    echo '    <td class="' . ($i % 2 == 0 ? 'high' : 'low') . 'light">' . ($i + 1) . ".</td>\n";
//  echo '    <td class="' . ($i % 2 == 1 ? 'high' : 'low') . 'light">(' . $song['id'] . ")</td>\n";
    echo '    <td class="' . ($i % 2 == 1 ? 'high' : 'low') . 'light' . ($is_playing ? '' : ' toxic_' . ($i % 2 == 0 ? 'brown' : 'green')) . '" style="text-align: right; margin: 0px; padding: 0px;">' . $song['title'] . "</td>\n";
    
    echo '    <td class="' . ($i % 2 == 1 ? 'high' : 'low') . 'light">';
    if (isset($song['artist']) && strlen($song['artist']) > 0)
      echo '&nbsp;by&nbsp;';
    echo "</td>\n";
    
    echo '    <td class="' /* "> */ . ($i % 2 == 1 ? 'high' : 'low') . 'light' . ($is_playing ? '' : ' toxic_' . ($i % 2 == 0 ? 'green' : 'brown')) . '" style="margin: 0px; padding: 0px;">';
    if (isset($song['artist']) && strlen($song['artist']) > 0)
      echo $song['artist'];
    echo "</td>\n";
    
    echo '    <td class="' . ($i % 2 == 0 ? 'high' : 'low') . 'light" style="color: #FFFFFF;">';
    if ($i > 0)
      echo '<a class="toxic_yellow" href="#" onclick="' . get_bump_js($i, $song['id'], 'up') . ' return false;">';
    echo '&nbsp;^&nbsp;';
    if ($i > 0)
      echo '</a>';
    echo "</td>\n";
    
    echo '    <td class="' . ($i % 2 == 0 ? 'high' : 'low') . 'light" style="color: #FFFFFF;">';
    if ($i < count($_SESSION['now_playing']['song_list']) - 1)
      echo '<a class="toxic_yellow" href="#" onclick="' . get_bump_js($i, $song['id'], 'down') . ' return false;">';
    echo '&nbsp;v&nbsp;';
    if ($i < count($_SESSION['now_playing']['song_list']) - 1)
      echo '</a>';
    echo "</td>\n";
    
    echo '    <td class="' . ($i % 2 == 0 ? 'high' : 'low') . 'light"><a class="toxic_yellow" href="#" onclick="'; // >
    echo "var fb = exec_cmd('now_playing', 'dequeue_song', 'id=" . $_SESSION['now_playing']['song_list'][$i]['id'] . '&index=' . $i . "', true, function(feedback) {alert(feedback)}); ";
    echo $refresh_song_js;
    echo "return false;\">&nbsp;x&nbsp;</a></td>\n";
    
    echo '    <td class="' . ($i % 2 == 0 ? 'high' : 'low') . 'light"><a href="download.php?id=' . $_SESSION['now_playing']['song_list'][$i]['id'] . '" target="tab">&nbsp;dl&nbsp;</a></td>' . "\n";
    
    echo "  </tr>\n";
  }
  echo '</table>';
}
?>