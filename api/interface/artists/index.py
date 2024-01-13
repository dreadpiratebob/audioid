from api.exceptions.http_base import BadRequestException
from api.logic.artists import get_artists
from api.models.db_models import Artist
from api.util.audioid.artists import GetArtistsQueryParams, GetArtistsOrderColumns
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath
from api.util.response_list_modifiers import FilterInfo, OrderByCol, OrderDirection, PageInfo

class Artists:
  def __init__(self, artists:[list, tuple]):
    artists_type_error = 'artists must be a list or tuple of artists.'
    if not isinstance(artists, (list, tuple)):
      raise TypeError(artists_type_error)
    
    for artist in artists:
      if not isinstance(artist, Artist):
        raise TypeError(artists_type_error)
    
    self.artists = artists

def get(environment:dict, headers:dict, path_params:dict, query_params:dict, body) -> Response:
  param_val_errors = {param.param_name: param.get_value(query_params) for param in GetArtistsQueryParams}
  grievances = []
  for pve in param_val_errors.values():
    if pve[1] is not None:
      grievances.append(str(pve[1]))
  
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  catalog_id = param_val_errors[GetArtistsQueryParams.CATALOG_ID.param_name][0]
  
  artist_name                    = param_val_errors[GetArtistsQueryParams.ARTIST_NAME.param_name][0]
  artist_name_has_wildcards      = param_val_errors[GetArtistsQueryParams.ARTIST_NAME_HAS_WILDCARDS.param_name][0]
  artist_name_is_case_sensitive  = param_val_errors[GetArtistsQueryParams.ARTIST_NAME_IS_CASE_SENSITIVE.param_name][0]
  artist_name_matches_diacritics = param_val_errors[GetArtistsQueryParams.ARTIST_NAME_MATCHES_DIACRITICS.param_name][0]
  artist_filter = FilterInfo(None, artist_name, artist_name_has_wildcards, artist_name_is_case_sensitive, artist_name_matches_diacritics, None)
  
  genre_id                      = param_val_errors[GetArtistsQueryParams.GENRE_ID.param_name][0]
  genre_name                    = param_val_errors[GetArtistsQueryParams.GENRE_NAME.param_name][0]
  genre_name_has_wildcards      = param_val_errors[GetArtistsQueryParams.GENRE_NAME_HAS_WILDCARDS.param_name][0]
  genre_name_is_case_sensitive  = param_val_errors[GetArtistsQueryParams.GENRE_NAME_IS_CASE_SENSITIVE.param_name][0]
  genre_name_matches_diacritics = param_val_errors[GetArtistsQueryParams.GENRE_NAME_MATCHES_DIACRITICS.param_name][0]
  genre_filter = FilterInfo(genre_id, genre_name, genre_name_has_wildcards, genre_name_is_case_sensitive, genre_name_matches_diacritics, None)
  if genre_id is not None and genre_name is not None:
    raise BadRequestException('only one of genre_id and genre_name can be set.')
  
  sort_asc    = param_val_errors[GetArtistsQueryParams.SORT_ASC.param_name][0]
  order_by    = [OrderByCol(GetArtistsOrderColumns.ARTIST_NAME, OrderDirection.ASCENDING if sort_asc else OrderDirection.DESCENDING)]
  page_number = param_val_errors[GetArtistsQueryParams.PAGE_NUMBER.param_name][0]
  page_size   = param_val_errors[GetArtistsQueryParams.PAGE_SIZE.param_name][0]
  page_info   = None
  if page_size is not None:
    try:
      page_info = PageInfo(page_number, page_size)
    except (ValueError, TypeError) as e:
      raise BadRequestException(str(e))
  
  include_tracks = param_val_errors[GetArtistsQueryParams.INCLUDE_TRACKS.param_name][0]
  include_albums = param_val_errors[GetArtistsQueryParams.INCLUDE_ALBUMS.param_name][0]
  include_album_tracks = param_val_errors[GetArtistsQueryParams.INCLUDE_ALBUM_TRACKS.param_name][0]
  include_genres = param_val_errors[GetArtistsQueryParams.INCLUDE_GENRES.param_name][0]
  
  artists = get_artists(catalog_id, artist_filter, genre_filter, order_by, page_info, include_tracks, include_albums, include_album_tracks, include_genres)
  
  if len(artists) == 0:
    return Response(None, HTTPStatusCodes.HTTP204)
  
  return Response(Artists(artists), HTTPStatusCodes.HTTP200, use_public_fields_only=False)

def get_help() -> AvailablePath:
  return AvailablePath(query_params=tuple(param for param in GetArtistsQueryParams), description='this endpoint lists artists in the given catalog, filtered by name or genre if requested and sorted and paginated as requested.')