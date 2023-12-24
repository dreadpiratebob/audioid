from api.dao.load_db_models import get_songs as get_songs_from_db
from api.util.response_list_modifiers import FilterInfo, OrderByCol, PageInfo

def get_song_for_download(song_id:int):
  pass

def get_songs(catalog_id:int, song:FilterInfo, song_year:int, artist:FilterInfo, album:FilterInfo, album_artist:FilterInfo, genre:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo):
  return get_songs_from_db(catalog_id, song, song_year, artist, album, album_artist, genre, order_by, page_info)