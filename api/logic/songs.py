from api.dao.load_db_models import FilterInfo,\
  get_songs as get_songs_from_db

def get_songs(catalog_id:int, song:FilterInfo, song_year:int, artist:FilterInfo, album:FilterInfo, album_artist:FilterInfo, genre:FilterInfo):
  return get_songs_from_db(catalog_id, song, song_year, artist, album, album_artist, genre)