<?php // >
$div_name      = (isset($what) && strlen($what) > 0 && strcmp($what, 'everything') != 0 ? 'browse_' . $what . '_list_div' : 'browse_div');
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
      <script type="text/javascript" src="js/browse.js"></script>
      <div id="<?=$div_name?>"></div>
      <script type="text/javascript">
        load_view('browse', 'browse', 'what=<?=($what . $filter_params)?>', document.getElementById('<?=$div_name?>'), function(){}, true);
      </script>