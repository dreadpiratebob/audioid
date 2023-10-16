from api.dao.load_db_models import get_songs as get_songs_from_db
def get_songs(catalog_id:int, song_name:str, song_year:int, artist_id:int, artist_name:str, artist_name_is_an_exact_match:bool,
              album_id:int, album_name:str, album_name_is_an_exact_match:bool, album_artist_id:int, album_artist_name:str,
              album_artist_name_is_an_exact_match:bool, genre_id:int, genre_name:str, genre_name_is_an_exact_match:bool):
  return get_songs_from_db(catalog_id, song_name, song_year, artist_id, artist_name, artist_name_is_an_exact_match,
                           album_id, album_name, album_name_is_an_exact_match, album_artist_id, album_artist_name, album_artist_name_is_an_exact_match,
                           genre_id, genre_name, genre_name_is_an_exact_match)