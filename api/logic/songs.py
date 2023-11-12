from api.dao.load_db_models import get_songs as get_songs_from_db
def get_songs(catalog_id:int, song_title:str, song_title_has_wildcards:bool, song_title_is_case_sensitive:bool, song_title_matches_diacritics:bool, song_year:int,
              artist_id:int, artist_name:str, artist_name_has_wildcards:bool, artist_name_is_case_sensitive:bool, artist_name_matches_diacritics:bool, filter_on_null_artist:bool,
              album_id:int, album_name:str, album_name_has_wildcards:bool, album_name_is_case_sensitive:bool, album_name_matches_diacritics:bool, filter_on_null_album:bool,
              album_artist_id:int, album_artist_name:str, album_artist_name_has_wildcards:bool, album_artist_name_is_case_sensitive:bool, album_artist_name_matches_diacritics:bool, filter_on_null_album_artist:bool,
              genre_id:int, genre_name:str, genre_name_is_an_exact_match:bool):
  return get_songs_from_db(catalog_id, song_title, song_title_has_wildcards, song_title_is_case_sensitive, song_title_matches_diacritics, song_year,
                           artist_id, artist_name, artist_name_has_wildcards, artist_name_is_case_sensitive, artist_name_matches_diacritics, filter_on_null_artist,
                           album_id, album_name, album_name_has_wildcards, album_name_is_case_sensitive, album_name_matches_diacritics, filter_on_null_album,
                           album_artist_id, album_artist_name, album_artist_name_has_wildcards, album_artist_name_is_case_sensitive, album_artist_name_matches_diacritics, filter_on_null_album_artist,
                           genre_id, genre_name, genre_name_is_an_exact_match)