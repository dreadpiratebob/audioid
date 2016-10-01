<?php // >

$what = $data['what'];
if (!isset($what) || ((strcmp($what, 'songs') != 0) && (strcmp($what, 'artists') != 0) && (strcmp($what, 'albums') != 0) && (strcmp($what, 'genres') != 0) && (strcmp($what, 'playlists') != 0) && (strcmp($what, 'catalogs') != 0)))
{
  $filter_params = '';
  
  $song_name = $_POST['song_name'];
  if (!isset($song_name) || strlen($song_name) <= 0)
    $song_name = $_GET['song_name'];
  if (isset($song_name) && strlen($song_name) > 0)
    $filter_params .= '&song_name=' . $song_name;
  
  $artist_name = $_POST['artist_name'];
  if (!isset($artist_name) || strlen($artist_name) <= 0)
    $artist_name = $_GET['artist_name'];
  if (isset($artist_name) && strlen($artist_name) > 0)
    $filter_params .= '&artist_name=' . $artist_name;
  
  $album_name = $_POST['album_name'];
  if (!isset($album_name) || strlen($album_name) <= 0)
    $album_name = $_GET['album_name'];
  if (isset($album_name) && strlen($album_name) > 0)
    $filter_params .= '&album_name=' . $album_name;
  
  $genre_name = $_POST['genre_name'];
  if (!isset($genre_name) || strlen($genre_name) <= 0)
    $genre_name = $_GET['genre_name'];
  if (isset($genre_name) && strlen($genre_name) > 0)
    $filter_params .= '&genre_name=' . $genre_name;
  
?>
    load_view('browse', 'browse', 'what=songs<?=$filter_params?>',   document.getElementById('browse_songs_list_div'),        function(feedback) {}, true);
    load_view('browse', 'browse', 'what=artists<?=$filter_params?>', document.getElementById('browse_artists_list_div'),      function(feedback) {}, true);
    load_view('browse', 'browse', 'what=albums<?=$filter_params?>',  document.getElementById('browse_albums_list_div'),       function(feedback) {}, true);
    load_view('browse', 'browse', 'what=genres<?=$filter_params?>',  document.getElementById('browse_genres_list_div'),       function(feedback) {}, true);
//    load_view('browse', 'browse', 'what=playlists<?=$filter_params?>',  document.getElementById('browse_playlists_list_div'), function(feedback) {}, true);
<?php // >
}

?>