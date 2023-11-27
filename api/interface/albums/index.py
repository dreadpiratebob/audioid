from api.exceptions.http_base import BadRequestException
from api.logic.albums import get_albums
from api.models.db_models import Album
from api.util.audioid.albums import GetAlbumsQueryParams, GetAlbumsOrderColumns
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath
from api.util.response_list_modifiers import FilterInfo, OrderByCol, OrderDirection, PageInfo

class Albums:
  def __init__(self, albums:[list, tuple]):
    catalogs_type_error = 'albums must be a list or tuple of albums.'
    if not isinstance(albums, (list, tuple)):
      raise TypeError(catalogs_type_error)
    
    for album in albums:
      if not isinstance(album, Album):
        raise TypeError(catalogs_type_error)
    
    self.albums = albums

def get(environment:dict, path_params:dict, query_params:dict, body) -> Response:
  param_val_errors = {param.param_name: param.get_value(query_params) for param in GetAlbumsQueryParams}
  grievances = []
  for pve in param_val_errors.values():
    if pve[1] is not None:
      grievances.append(str(pve[1]))
  
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  catalog_id = param_val_errors[GetAlbumsQueryParams.CATALOG_ID.param_name][0]
  
  album_artist_id                      = param_val_errors[GetAlbumsQueryParams.ALBUM_ARTIST_ID.param_name][0]
  album_artist_name                    = param_val_errors[GetAlbumsQueryParams.ALBUM_ARTIST_NAME.param_name][0]
  album_artist_name_has_wildcards      = param_val_errors[GetAlbumsQueryParams.ALBUM_ARTIST_NAME_HAS_WILDCARDS.param_name][0]
  album_artist_name_is_case_sensitive  = param_val_errors[GetAlbumsQueryParams.ALBUM_ARTIST_NAME_IS_CASE_SENSITIVE.param_name][0]
  album_artist_name_matches_diacritics = param_val_errors[GetAlbumsQueryParams.ALBUM_ARTIST_NAME_MATCHES_DIACRITICS.param_name][0]
  filter_on_null_album_artist          = param_val_errors[GetAlbumsQueryParams.FILTER_ON_NULL_ALBUM_ARTIST.param_name][0]
  album_artist_filter = FilterInfo(album_artist_id, album_artist_name, album_artist_name_has_wildcards, album_artist_name_is_case_sensitive, album_artist_name_matches_diacritics, filter_on_null_album_artist)
  
  sort_asc    = param_val_errors[GetAlbumsQueryParams.ORDER_BY.param_name][0]
  order_by    = [OrderByCol(GetAlbumsOrderColumns.ALBUM_ARTIST_NAME, OrderDirection.ASCENDING if sort_asc else OrderDirection.DESCENDING)]
  page_number = param_val_errors[GetAlbumsQueryParams.PAGE_NUMBER.param_name][0]
  page_size   = param_val_errors[GetAlbumsQueryParams.PAGE_SIZE.param_name][0]
  page_info   = None
  if page_size is not None:
    try:
      page_info = PageInfo(page_number, page_size)
    except (ValueError, TypeError) as e:
      raise BadRequestException(str(e))
  
  include_tracks = param_val_errors[GetAlbumsQueryParams.INCLUDE_TRACKS.param_name][0]
  include_albums = param_val_errors[GetAlbumsQueryParams.INCLUDE_ALBUMS.param_name][0]
  include_album_tracks = param_val_errors[GetAlbumsQueryParams.INCLUDE_ALBUM_TRACKS.param_name][0]
  include_genres = param_val_errors[GetAlbumsQueryParams.INCLUDE_GENRES.param_name][0]
  
  artists = get_artists(catalog_id, album_artist_filter, genre_filter, order_by, page_info, include_tracks, include_albums, include_album_tracks, include_genres)
  
  if len(artists) == 0:
    return Response(None, HTTPStatusCodes.HTTP204)
  
  return Response(Albums(artists), HTTPStatusCodes.HTTP200, use_public_fields_only=False)

def get_help() -> AvailablePath:
  return AvailablePath(query_params=tuple(param for param in GetAlbumsQueryParams), description='this endpoint lists artists in the given catalog, filtered by name or genre if requested and sorted and paginated as requested.')