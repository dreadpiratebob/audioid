from api.dao.load_db_models import get_artists as get_db_artists
from api.util.audioid.artists import IncludeAlbumModes
from api.util.response_list_modifiers import FilterInfo, OrderByCol, PageInfo

def get_artists(catalog_id:int, artist_filter:FilterInfo, genre_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo,
                include_songs:bool = False, include_albums:IncludeAlbumModes = IncludeAlbumModes.ALBUM_ARTIST_ONLY, include_album_tracks:bool = False, include_genres:bool = False):
  return get_db_artists(catalog_id, artist_filter, genre_filter, order_by, page_info, include_songs, include_albums, include_album_tracks, include_genres)