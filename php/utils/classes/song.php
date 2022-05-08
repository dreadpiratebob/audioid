<?php

include('php/utils/classes/catalog.php');
include('php/utils/classes/album.php');
include('php/utils/classes/genre.php');

class song
{
  private $id           = null;
  private $name         = null;
  private $year         = null;
  private $filename     = null;
  private $artist_names = null;
  
  private $album        = null;
  private $genre        = null;
  private $catalog      = null;
  
  public function __construct($id, $other_data)
  {
    if (!isset($id))
    {
      return;
    }
    
    if (!is_numeric($id))
    {
      throw new Exception("Invalid ID '{$id}'.  An ID must be a whole number.");
    }
    
    $id = intval($id);
    if (is_array($other_data))
    {
      build_from_array($id, $other_data);
    }
    else
    {
      build_from_sql($id, $other_data);
    }
  }
  
  private function build_from_sql($id, $sql_link)
  {
    $query    = "SELECT s.id AS song_id, s.name AS song_name, s.year AS song_year, s.filename AS song_filename,\n" .
                "  c.id AS catalog_id, c.name AS catalog_name,\n" .
                "  al.id AS album_id, al.name AS album_name, al.album_artist AS album_artist" .
                "  g.id AS genre_id, g.name AS genre_name,\n" .
                "  GROUP_CONCAT(ar.name, s_ar.conjunction SEPARATOR '' ORDER BY s_ar.list_order)\n" .
                "FROM songs AS s\n" .
                "  INNER JOIN catalogs AS c ON c.id = s.catalog_id\n" .
                "  INNER JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n" .
                "  INNER JOIN artists AS ar ON ar.id = s_ar.artist_id\n" .
                "  INNER JOIN songs_albums AS s_al ON s_al.song_id = s.id\n" .
                "  INNER JOIN albums AS al ON al.id = s_al.id\n" .
                "  INNER JOIN songs_genres AS s_g ON s_g.song_id = s.id\n" .
                "  INNER JOIN genres AS g ON g.id = s_g.genre_id\n" .
                "GROUP BY s.id\n" .
                "WHERE s.id = {$id};"
    $sql_song = $sql_link->query($query);
    
    if ($sql_song === false)
    {
      $query = str_replace("\n", "<br />\n", $query);
      throw new Exception("query died.<br />\n<br />\nquery:<br />\n{$query}<br />\n<br />\nerror:<br />\n{$sql_link->errorInfo()[2]}")
    }
    
    if ($sql_song->rowCount() === 0)
    {
      return;
    }
    
    $arr_song = $sql_song->fetch(PDO::FETCH_ASSOC);
    build_from_array($arr_song);
  }
  
  private function build_from_array($id, $arr_song)
  {
    $id           = $arr_song['song_id'];
    $name         = $arr_song['song_name'];
    $year         = $arr_song['song_year'];
    $filename     = $arr_song['song_filename'];
    $artist_names = $arr_song['song_artist_names'];
    
    $album        = new album($arr_song);
    $genre        = new genre($arr_song);
    $catalog      = new catalog($arr_song);
  }
}

?>