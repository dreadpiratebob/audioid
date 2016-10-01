<?php // >
if (isset($data['refresh']) && strcmp($data['refresh'], 'true') == 0)
{
?>
    var refresh_song_list = function ()
    {
      var view_div   = document.getElementById('now_playing_song_list_div');
      var on_load_fn = function()
      {
      };
      
      load_view('now_playing', 'song_list', 'refresh=true', view_div, on_load_fn, true, true);
    };
    
    setTimeout(refresh_song_list, 5000);
<?php // >
}
?>