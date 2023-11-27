from api.util.functions import parse_bool
from api.util.http import QueryParam
from api.util.response_list_modifiers import \
  OrderByCol, OrderColName, OrderDirection, \
  get_order_parser, parse_page_size

from enum import Enum

class GetAlbumsOrderColumns(OrderColName):
  ALBUM_NAME = 'album_name', 'the album\'s name'
  ALBUM_ARTIST_NAME = 'album_artist_name', 'the album artist\'s name'

get_albums_order_columns_by_column_name = {col.column_name: col for col in GetAlbumsOrderColumns}
default_get_albums_order_by = tuple \
(
  [
    OrderByCol(GetAlbumsOrderColumns.ALBUM_ARTIST_NAME, OrderDirection.ASCENDING),
    OrderByCol(GetAlbumsOrderColumns.ALBUM_NAME, OrderDirection.ASCENDING)
  ]
)

class GetAlbumsQueryParams(QueryParam):
  CATALOG_ID  = 'catalog_id',  True,  int, 'integer', 'an integer', None, 'the id of the catalog to search'
  ALBUM_NAME = 'album_name', False, str, 'string', 'a string',   None, 'the name of the album to get'
  ALBUM_NAME_HAS_WILDCARDS      = 'album_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if album_name isn\'t set, album_name_has_wildcards is ignored.  if album_name_has_wildcards is true, % and _ in album_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if album_name_has_wildcards is false, % and _ will be treated literally.'
  ALBUM_NAME_IS_CASE_SENSITIVE  = 'album_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if album_name isn\'t set, album_name_is_case_sensitive is ignored.  if album_name_is_case_sensitive is true, letters in album_name will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  ALBUM_NAME_MATCHES_DIACRITICS = 'album_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if album_name isn\'t set, album_name_matches_diacritics is ignored.  if album_name_matches_diacritics is true, letters in album_name will be matched exactly; otherwise, diacritics will be stripped out of both the album_name parameter and album\'s name, so "a" in the query parameter will match "ä", "à", "å", etc. in the album name.'
  ALBUM_ARTIST_ID   = 'album_artist_id',   False, int, 'integer', 'an integer', None, 'the id of the album artist whose albums to get'
  ALBUM_ARTIST_NAME = 'album_artist_name', False, str, 'string',  'a string',   None, 'the name of the album artist(s) whose albums to get'
  ALBUM_ARTIST_NAME_HAS_WILDCARDS      = 'album_artist_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if album_artist_name isn\'t set, album_artist_name_has_wildcards is ignored.  if album_artist_name_has_wildcards is true, % and _ in artist_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if album_artist_name_has_wildcards is false, % and _ will be treated literally.'
  ALBUM_ARTIST_NAME_IS_CASE_SENSITIVE  = 'album_artist_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if album_artist_name isn\'t set, album_artist_name_is_case_sensitive is ignored.  if album_artist_name_is_case_sensitive is true, letters in artist_name will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  ALBUM_ARTIST_NAME_MATCHES_DIACRITICS = 'album_artist_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if album_artist_name isn\'t set, album_artist_name_matches_diacritics is ignored.  if album_artist_name_matches_diacritics is true, letters in album_artist_name will be matched exactly; otherwise, diacritics will be stripped out of both the album_artist_name parameter and the album artist\'s name, so "a" in the query parameter will match "ä", "à", "å", etc. in the album artist name.'
  FILTER_ON_NULL_ALBUM_ARTIST          = 'filter_on_null_album_artist',          False, parse_bool, 'boolean', 'a boolean', False, 'if album_artist_id or album_artist_name is set, filter_on_null_album_artist is ignored.  if filter_on_null_album_artist is true, only albums without an album artist will be returned; otherwise, albums will be returned regardless of whether they have an album artist.'
  ORDER_BY    = 'order_by',    False, get_order_parser(GetAlbumsOrderColumns, get_albums_order_columns_by_column_name), 'a list of album order columns', 'a list of album order columns', default_get_albums_order_by, 'this must be a comma separated list of column/direction pairs, eg "album_name asc, album_artist_name desc". if a column\'s direction is omitted, it will default to ascending.  these columns are available: %s; a direction must be "ascending" (or "asc") or "descending" (or "desc").' % (', '.join(['%s (%s)' % (ob_col.column_name, ob_col.description) for ob_col in GetAlbumsOrderColumns]), )
  PAGE_NUMBER = 'page_number', False, int, 'integer', 'an integer', 1, 'the 1-based number of which page to get; e.g. if you\'re getting 50 results at a time and you want results #51-100, this would be 2.'
  PAGE_SIZE   = 'page_size',   False, parse_page_size, 'integer', 'an integer', 100, 'the size of one page; i.e. the maximum number of results to get.  if this is "all", all results will be returned regardless of what the value of page_number is.'
  INCLUDE_TRACKS = 'include_tracks', False, parse_bool, 'boolean', 'a boolean', False, 'if true, all of each artist\'s tracks will be returned along with the rest of the information about each artist.'