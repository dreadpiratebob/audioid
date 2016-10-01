<table>
  <tr>
    <td>
      song title:
    </td>
    <td>
      <input type="text" id="song_txt" size="60" />
    </td>
    <td>
      &nbsp;
    </td>
  </tr>
    <tr>
    <td>
      artist name:
    </td>
    <td>
      <input type="text" id="artist_txt" size="60" />
    </td>
    <td>
      <div id="no_artist_div" onclick="chk_empty('artist');" class="toxic_yellow">
        search for empty artists? <div id="no_artist_chk" class="toxic_brown" style="display:inline">N</div>
      </div>
    </td>
  </tr>
    <tr>
    <td>
      album name:
    </td>
    <td>
      <input type="text" id="album_txt" size="60" />
    </td>
    <td>
      <div id="no_album_div" onclick="chk_empty('album');" class="toxic_yellow">
        search for empty albums? <div id="no_album_chk" class="toxic_brown" style="display:inline">N</div>
      </div>
    </td>
  </tr>
  <tr>
    <td>
      genre:
    </td>
    <td>
      <input type="text" id="genre_txt" size="60" />
    </td>
    <td>
      <div id="no_genre_div" onclick="chk_empty('genre');" class="toxic_yellow">
        search for empty genres? <div id="no_genre_chk" class="toxic_brown" style="display:inline">N</div>
      </div>
    </td>
  </tr>
</table>
<button type="button" id="song_btn" onclick="filter('song');">filter songs</button>&nbsp;
<button type="button" id="artist_btn" onclick="filter('artist');">filter artists</button>&nbsp;
<button type="button" id="album_btn" onclick="filter('album');">filter albums</button>&nbsp;
<button type="button" id="genre_btn" onclick="filter('genre');">filter genres</button>