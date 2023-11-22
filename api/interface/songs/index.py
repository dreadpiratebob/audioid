from api.util.response_list_modifiers import FilterInfo, PageInfo
from api.exceptions.http_base import BadRequestException
from api.logic.songs import get_songs
from api.models.db_models import Song
from api.util.audioid.songs import GetSongsQueryParams
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath

class Songs:
  def __init__(self, songs:[list, tuple]):
    songs_type_error = 'songs must be a list or tuple of songs.'
    if not isinstance(songs, (list, tuple)):
      raise TypeError(songs_type_error)
    
    for song in songs:
      if not isinstance(song, Song):
        raise TypeError(songs_type_error)
    
    self.songs = songs

def get(environment:dict, path_params:dict, query_params:dict, body) -> Response:
  param_val_errors = {param.param_name: param.get_value(query_params) for param in GetSongsQueryParams}
  params = {param_name: param_val_errors[param_name][0] for param_name in param_val_errors}
  grievances = []
  for pve in param_val_errors.values():
    if pve[1] is not None:
      grievances.append(str(pve[1]))
  
  album_id = params[GetSongsQueryParams.ALBUM_ID.param_name]
  album_name = params[GetSongsQueryParams.ALBUM_NAME.param_name]
  album_name_has_wildcards      = params[GetSongsQueryParams.ALBUM_NAME_HAS_WILDCARDS.param_name]
  album_name_is_case_sensitive  = params[GetSongsQueryParams.ALBUM_NAME_IS_CASE_SENSITIVE.param_name]
  album_name_matches_diacritics = params[GetSongsQueryParams.ALBUM_NAME_MATCHES_DIACRITICS.param_name]
  filter_on_null_album          = params[GetSongsQueryParams.FILTER_ON_NULL_ALBUM.param_name]
  album_filter = FilterInfo(album_id, album_name, album_name_has_wildcards, album_name_is_case_sensitive, album_name_matches_diacritics, filter_on_null_album)
  if album_id is not None and album_name is not None:
    grievances.append('only one query parameter of "album_id" and "album_name" per request can be set.')
  
  album_artist_id   = params[GetSongsQueryParams.ALBUM_ARTIST_ID.param_name]
  album_artist_name = params[GetSongsQueryParams.ALBUM_ARTIST_NAME.param_name]
  album_artist_name_has_wildcards      = params[GetSongsQueryParams.ALBUM_ARTIST_NAME_HAS_WILDCARDS.param_name]
  album_artist_name_is_case_sensitive  = params[GetSongsQueryParams.ALBUM_ARTIST_NAME_IS_CASE_SENSITIVE.param_name]
  album_artist_name_matches_diacritics = params[GetSongsQueryParams.ALBUM_ARTIST_NAME_MATCHES_DIACRITICS.param_name]
  filter_on_null_album_artist          = params[GetSongsQueryParams.FILTER_ON_NULL_ALBUM_ARTIST.param_name]
  album_artist_filter = FilterInfo(album_artist_id, album_artist_name, album_artist_name_has_wildcards, album_artist_name_is_case_sensitive, album_artist_name_matches_diacritics, filter_on_null_album_artist)
  if album_artist_id is not None and album_artist_name is not None:
    grievances.append('only one query parameter of "album_artist_id" and "album_artist_name" can be set.')
  
  artist_id   = params[GetSongsQueryParams.ARTIST_ID.param_name]
  artist_name = params[GetSongsQueryParams.ARTIST_NAME.param_name]
  artist_name_has_wildcards      = params[GetSongsQueryParams.ARTIST_NAME_HAS_WILDCARDS.param_name]
  artist_name_is_case_sensitive  = params[GetSongsQueryParams.ARTIST_NAME_IS_CASE_SENSITIVE.param_name]
  artist_name_matches_diacritics = params[GetSongsQueryParams.ARTIST_NAME_MATCHES_DIACRITICS.param_name]
  filter_on_null_artist          = params[GetSongsQueryParams.FILER_ON_NULL_ARTIST.param_name]
  artist_filter = FilterInfo(artist_id, artist_name, artist_name_has_wildcards, artist_name_is_case_sensitive, artist_name_matches_diacritics, filter_on_null_artist)
  if artist_id is not None and artist_name is not None:
    grievances.append('only one query parameter of "artist_id" and "artist_name" can be set.')
  
  genre_id   = params[GetSongsQueryParams.GENRE_ID.param_name]
  genre_name = params[GetSongsQueryParams.GENRE_NAME.param_name]
  genre_name_has_wildcards      = params[GetSongsQueryParams.GENRE_NAME_HAS_WILDCARDS.param_name]
  genre_name_is_case_sensitive  = params[GetSongsQueryParams.GENRE_NAME_IS_CASE_SENSITIVE.param_name]
  genre_name_matches_diacritics = params[GetSongsQueryParams.GENRE_NAME_MATCHES_DIACRITICS.param_name]
  filter_on_null_genre          = params[GetSongsQueryParams.FILTER_ON_NULL_GENRE.param_name]
  genre_filter = FilterInfo(genre_id, genre_name, genre_name_has_wildcards, genre_name_is_case_sensitive, genre_name_matches_diacritics, filter_on_null_genre)
  if genre_id is not None and genre_name is not None:
    grievances.append('only one query parameter of "genre_id" and "genre_name" can be set.')
  
  catalog_id = params[GetSongsQueryParams.CATALOG_ID.param_name]
  if not isinstance(catalog_id, int) or catalog_id < 0:
    grievances.append('a catalog id must be a nonnegative int.')
  
  song_title = params[GetSongsQueryParams.SONG_TITLE.param_name]
  song_title_has_wildcards      = params[GetSongsQueryParams.SONG_TITLE_HAS_WILDCARDS.param_name]
  song_title_is_case_sensitive  = params[GetSongsQueryParams.SONG_TITLE_IS_CASE_SENSITIVE.param_name]
  song_title_matches_diacritics = params[GetSongsQueryParams.SONG_TITLE_MATCHES_DIACRITICS.param_name]
  song_year = params[GetSongsQueryParams.SONG_YEAR.param_name]
  song_filter = FilterInfo(None, song_title, song_title_has_wildcards, song_title_is_case_sensitive, song_title_matches_diacritics, False)
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  order_by    = params[GetSongsQueryParams.ORDER_BY.param_name]
  page_number = params[GetSongsQueryParams.PAGE_NUMBER.param_name]
  page_size   = params[GetSongsQueryParams.PAGE_SIZE.param_name]
  page_info   = None
  if page_size is not None:
    try:
      page_info = PageInfo(page_number, page_size)
    except (ValueError, TypeError) as e:
      raise BadRequestException(str(e))
  
  songs = get_songs(catalog_id, song_filter, song_year, artist_filter, album_filter, album_artist_filter, genre_filter, order_by, page_info)
  
  if len(songs) == 0:
    return Response(None, HTTPStatusCodes.HTTP204)
  
  return Response(Songs(songs), HTTPStatusCodes.HTTP200, use_public_fields_only=False)

def get_help() -> AvailablePath:
  return AvailablePath(query_params=tuple(param for param in GetSongsQueryParams), description='this endpoint lists available songs, filtered, sorted and paginated as requested.')