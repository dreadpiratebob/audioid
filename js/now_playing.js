var play_window = null;
function load_play_window()
{
  if (play_window != null)
    return;
  
  play_window = window.open('play_music.php');
}