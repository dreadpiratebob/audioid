from api.util.functions import parse_bool
from api.util.http import QueryParam
from api.util.response_list_modifiers import OrderByCol, OrderColName, OrderDirection, parse_page_size

from enum import Enum

class GetArtistsOrderColumns(OrderColName):
  ARTIST_NAME = 'artist_name', 'the artist\'s name'

get_artists_order_columns_by_column_name = {col.column_name: col for col in GetArtistsOrderColumns}
default_get_artists_order_by = tuple \
(
  [
    OrderByCol(GetArtistsOrderColumns.ARTIST_NAME, OrderDirection.ASCENDING)
  ]
)

class IncludeAlbumModes(Enum):
  def __new__(self, *args, **kwds):
    value = len(self.__members__) + 1
    obj = object.__new__(self)
    obj._value_ = value
    return obj
  
  def __init__(self, param_val:str, description:str):
    self.param_val   = param_val
    self.description = description
  
  NO_ALBUMS         = 'none', 'don\'t get any of the artist\'s albums'
  ALBUM_ARTIST_ONLY = 'album_artist', 'get only those albums where the artist is the album\'s album artist.'
  ALL_ALBUMS        = 'all', 'get any albums where the artist is the album\'s album artist or the artist has at least one track on the album.'

include_album_modes_by_param_val = {mode.param_val: mode for mode in IncludeAlbumModes}
def parse_include_album_mode(param_val:str) -> IncludeAlbumModes:
  if not isinstance(param_val, str):
    raise TypeError('an include album mode can only be parsed from a string.')
  
  return include_album_modes_by_param_val.get(param_val, IncludeAlbumModes.ALBUM_ARTIST_ONLY)

class GetArtistsQueryParams(QueryParam):
  CATALOG_ID  = 'catalog_id',  True,  int, 'integer', 'an integer', None, 'the id of the catalog to search'
  ARTIST_NAME = 'artist_name', False, str, 'string', 'a string',   None, 'the name of the artists to get'
  ARTIST_NAME_HAS_WILDCARDS      = 'artist_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True, 'if artist_name isn\'t set, artist_name_has_wildcards is ignored.  if artist_name_has_wildcards is true, % and _ in artist_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if artist_name_has_wildcards is false, % and _ will be treated literally.'
  ARTIST_NAME_IS_CASE_SENSITIVE  = 'artist_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if artist_name isn\'t set, artist_name_is_case_sensitive is ignored.  if artist_name_is_case_sensitive is true, letters in artist_name will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  ARTIST_NAME_MATCHES_DIACRITICS = 'artist_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if artist_name isn\'t set, artist_name_matches_diacritics is ignored.  if artist_name_matches_diacritics is true, letters in artist_name will be matched exactly; otherwise, diacritics will be stripped out of both the artist_name parameter and artist\'s name, so "a" in the query parameter will match "ä", "à", "å", etc. in the artist name.'
  GENRE_ID   = 'genre_id',   False, str, 'string', 'a string', None, 'the id of the genre to filter by; only one of genre_id and genre_name can be set.'
  GENRE_NAME = 'genre_name', False, str, 'string', 'a string', None, 'the name of the genres to filter by; only one of genre_id and genre_name can be set.'
  GENRE_NAME_HAS_WILDCARDS      = 'genre_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if genre_name isn\'t set, genre_name_has_wildcards is ignored.  if genre_name_has_wildcards is true, % and _ in genre_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if genre_name_has_wildcards is false, % and _ will be treated literally.'
  GENRE_NAME_IS_CASE_SENSITIVE  = 'genre_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if genre_name isn\'t set, genre_name_is_case_sensitive is ignored.  if genre_name_is_case_sensitive is true, letters in genre_name will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  GENRE_NAME_MATCHES_DIACRITICS = 'genre_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if genre_name isn\'t set, genre_name_matches_diacritics is ignored.  if genre_name_matches_diacritics is true, letters in genre_name will be matched exactly; otherwise, diacritics will be stripped out of both the genre_name parameter and genre\'s name, so "a" in the query parameter will match "ä", "à", "å", etc. in the genre name.'
  SORT_ASC    = 'sort_asc',    False, parse_bool, 'boolean', 'a boolean', True, 'if true, the resulting list will be sorted in alphabetical order by artist name.  otherwise, it\'ll be sorted in reverse alphabetical order.'
  PAGE_NUMBER = 'page_number', False, int, 'integer', 'an integer', 1, 'the 1-based number of which page to get; e.g. if you\'re getting 50 results at a time and you want results #51-100, this would be 2.'
  PAGE_SIZE   = 'page_size',   False, parse_page_size, 'integer', 'an integer', 100, 'the size of one page; i.e. the maximum number of results to get.  if this is "all", all results will be returned regardless of what the value of page_number is.'
  INCLUDE_TRACKS = 'include_tracks', False, parse_bool, 'boolean', 'a boolean', False, 'if true, all of each artist\'s tracks will be returned along with the rest of the information about each artist.'
  INCLUDE_ALBUMS = 'include_albums', False, parse_include_album_mode, 'include album mode', 'an include album mode', IncludeAlbumModes.ALBUM_ARTIST_ONLY, ('this specifies which albums to get for each artist, and can be one of these values: %s' % (', '.join(['%s (%s)' % (mode.param_val, mode.description) for mode in IncludeAlbumModes]), ))
  INCLUDE_ALBUM_TRACKS = 'include_album_tracks', False, parse_bool, 'boolean', 'a boolean', False, 'if include_albums is "none", this parameter will be ignored.  otherwise, if include_album_tracks is true, all of each album\'s tracks will be returned along with the rest of the information about each album.'
  INCLUDE_GENRES = 'include_genres', False, parse_bool, 'boolean', 'a boolean', False, 'if include_genres is true, all of each artist\'s genres will be returned along with the rest of the information about each artist.'