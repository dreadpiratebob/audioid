      <script type="text/javascript" src="js/browse.js"></script>
      <script type="text/javascript" src="js/search.js"></script>
      <div id="search_div"></div>
      <br />
      <div id="browse_artists_div">
        <a href="#" id="show_hide_artists_lnk" class="show_hide" onclick="show_hide_browse_lists('artists'); return false;">+artists</a><br />
        <div id="browse_artists_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
      </div>
      <div id="browse_albums_div">
        <a href="#" id="show_hide_albums_lnk" class="show_hide" onclick="show_hide_browse_lists('albums'); return false;">+albums</a><br />
        <div id="browse_albums_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
      </div>
      <div id="browse_genres_div">
        <a href="#" id="show_hide_genres_lnk" class="show_hide" onclick="show_hide_browse_lists('genres'); return false;">+genres</a><br />
        <div id="browse_genres_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
      </div>
      <!---
      <div id="browse_playlists_div">
        <a href="#" id="show_hide_playlists_lnk" class="show_hide" onclick="show_hide_browse_lists('playlists'); return false;">+playlists</a><br />
        <div id="browse_playlists_list_div" style="display: none; border-bottom: 1px solid #FFAA30;"></div>
      </div>
      --->
      <div id="browse_songs_div">
        <a href="#" id="show_hide_songs_lnk" class="show_hide" onclick="show_hide_browse_lists('songs'); return false;">-songs</a><br />
        <div id="browse_songs_list_div"></div>
      </div>
      <script type="text/javascript">
        load_view('browse', 'browse', 'what=songs&song_name=<?=$_POST['search_txt']?>',         document.getElementById('browse_songs_list_div'),     function () {}, true);
        load_view('browse', 'browse', 'what=artists&artist_name=<?=$_POST['search_txt']?>',     document.getElementById('browse_artists_list_div'),   function () {}, true);
        load_view('browse', 'browse', 'what=albums&album_name=<?=$_POST['search_txt']?>',       document.getElementById('browse_albums_list_div'),    function () {}, true);
        load_view('browse', 'browse', 'what=genres&genre_name=<?=$_POST['search_txt']?>',       document.getElementById('browse_genres_list_div'),    function () {}, true);
      //load_view('browse', 'browse', 'what=playlists&playlist_name=<?=$_POST['search_txt']?>', document.getElementById('browse_playlists_list_div'), function () {}, true);
        load_view('search', 'search', '',                                                       document.getElementById('search_div'),                function () {}, true);
      </script>