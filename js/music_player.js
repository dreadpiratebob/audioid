function load_page(now_playing_id, has_next)
{
  window.playing = 1;
  
  document.getElementById('audio_2').load();
  window.should_play_next = has_next;
  
  var tmp = document.title.split(' ');
  window.pre_title = '';
  for (var i = 0; i < tmp.length - 1; ++i)
    window.pre_title += (tmp[i] + ' ');
  
  var check_list = function()
  {
    load_view('play_music', 'next_two_songs', '', document.getElementById('check_list'), function(feedback) {}, true, true, function(feedback) {});
  };
  setTimeout(check_list, 1000);
}

function skip_to_next(next)
{
  if (next != 2)
    next = 1;
  
  var current = (next == 1 ? 2 : 1);
  
  window.playing = current;
  
  if (window.should_play_next)
    document.getElementById('audio_' + next).play();
  
  var part1 = function(feedback)
  {
    exec_cmd('play_music', 'get_song_data', 'offset=0', false, part2);
  };
  
  var part2 = function(feedback)
  {
    var song = null;
    eval('song = ' + feedback + ';');
    
    if (song == null) // no music left
    {
      document.title = (window.pre_title + ' [stopped]');
      
      return;
    }
    
    window.pre_title = (song.title + (song.artist == null ? '' : ' by ' + song.artist));
    document.title   = (window.pre_title + ' [playing]');
    
    exec_cmd('play_music', 'get_song_data', 'offset=1', false, part3);
  };
  
  var part3 = function(feedback)
  {
    var song = null;
    eval('song = ' + feedback + ';');
    
    if (song == null)
    {
      window.should_play_next = false;
      return;
    }
    
    document.getElementById('audio_src_' + current).src = 'embed.php?id=' + song.id;
    document.getElementById('audio_' + current).load();
  };
  
  exec_cmd('now_playing', 'increment_current_song', 'default=0', false, part1);
}

function on_pause(which) // which one on the off chance i care sometime
{
  if (window.pre_title != undefined)
    document.title = window.pre_title + ' [paused]';
}

function on_play(which) // which one on the off chance i care sometime
{
  if (window.pre_title != undefined)
    document.title = window.pre_title + ' [playing]';
}