from api.dao.load_db_models import get_albums as get_db_albums
from api.util.response_list_modifiers import FilterInfo, OrderByCol, PageInfo

def get_albums(catalog_id:int, album_filter:FilterInfo, track_artist_filter:FilterInfo, album_artist_filter:FilterInfo, genre_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo, include_tracks:bool = False):
  return get_db_albums(catalog_id, album_filter, track_artist_filter, album_artist_filter, genre_filter, order_by, page_info, include_tracks)