    var fb      = ('playing: ' + window.playing + '\n\n');
    var current = window.playing;
    var next    = (window.playing == 2 ? 1 : 2);
    fb += ('current: ' + current + '\nnext: ' + next + '\n\n');
    
    var new_ids = document.getElementById('check_list').innerHTML.split('/');
    new_ids[0]  = parseInt(new_ids[0]);
    new_ids[1]  = parseInt(new_ids[1]);
    
    var audio1  = document.getElementById('audio_' + current);
    var audio2  = document.getElementById('audio_' + next);
    var src1    = document.getElementById('audio_src_' + current);
    var src2    = document.getElementById('audio_src_' + next);
    var tmp     = src1.src;
    tmp         = tmp.split('?id=');
    var old_id1 = parseInt(tmp[1]);
    
    tmp         = src2.src;
    tmp         = tmp.split('?id=');
    var old_id2 = parseInt(tmp[1]);
    
    if (isNaN(new_ids[0]))
    {
      fb += 'first new id isNaN\n\n';
      audio1.pause();
      document.body.removeChild(audio1);
      document.body.appendChild(audio1);
    }
    else if (new_ids[0] != old_id1)
    {
      fb += 'first new id is new (was ' + old_id1 + '; is ' + new_ids[0] + ')\n';
      // a new song should be playing; load it into the next player & play it.
      src2.src = 'embed.php?id=' + new_ids[0];
      
      document.body.removeChild(audio2);
      document.body.appendChild(audio2);
      
      audio1.pause();
      audio2.play();
      
      document.body.removeChild(audio1);
      document.body.appendChild(audio1);
      
      tmp            = next;
      next           = current;
      current        = tmp;
      window.playing = current;
      
      audio1  = document.getElementById('audio_' + current);
      audio2  = document.getElementById('audio_' + next);
      src1    = document.getElementById('audio_src_' + current);
      src2    = document.getElementById('audio_src_' + next);
      fb += ('current: ' + current + '\nnext: ' + next + '\n\n');
      
      var song_data = JSON.parse(exec_cmd('play_music', 'get_song_data', 'offset=0', true));
      window.pre_title = song_data.title;
      if (song_data.artist != null)
        window.pre_title += ' by ' + song_data.artist;
      document.title = window.pre_title + ' [playing]';
    }
    
    if (isNaN(new_ids[1]))
    {
      fb += ('second new id isNaN\n');
      audio1.onended = function()
      {
        
      }
    }
    else if (new_ids[1] != old_id2)
    {
      fb += 'second new id is new\n';
      var local_tmp = (window.playing == 2 ? 1 : 2);
      audio1.onended = function()
      {
        skip_to_next(local_tmp);
      }
      
      var local_current = (window.playing == 2 ? 2 : 1);
      var local_next    = (window.playing == 2 ? 1 : 2);
      
      document.body.removeChild(audio2);
      audio2          = null;
      audio2          = document.createElement('audio');
      audio2.id       = ('audio_' + local_next);
      audio2.controls = true;
      audio2.autoplay = false;
      audio2.loop     = false;
      
      audio2.onended  = function()
      {
        skip_to_next(local_current);
      };
      
      audio2.onpause  = function()
      {
        on_pause(local_next);
      };
      
      audio2.onplay   = function()
      {
        on_play(local_next);
      };
      
      src2      = null;
      src2      = document.createElement('source');
      src2.id   = 'audio_src_' + local_next;
      src2.src  = 'embed.php?id=' + new_ids[1];
      src2.type = 'audio/mpeg';
      
      audio2.appendChild(src2);
      audio2.appendChild(document.createTextNode('your browse doesn\'t support &lt;audio&gt; tags.'));
      document.body.appendChild(audio2);
    }
//    alert(fb);
    var check_list = function()
    {
      load_view('play_music', 'next_two_songs', '', document.getElementById('check_list'), function(feedback) {}, true, true, function(feedback) {});
    };
    setTimeout(check_list, 1500);