from api.util.functions import parse_bool
from api.util.http import QueryParam
from api.util.response_list_modifiers import OrderByCol, OrderColName, OrderDirection, parse_page_size

class GetGenresOrderColumns(OrderColName):
  GENRE_NAME = None, 'genre_name', 'the genre\'s name'

get_genres_order_columns_by_column_name = {col.column_name: col for col in GetGenresOrderColumns}
default_get_genres_order_by = tuple \
(
  [
    OrderByCol(GetGenresOrderColumns.GENRE_NAME, OrderDirection.ASCENDING)
  ]
)

class GetGenresQueryParams(QueryParam):
  CATALOG_ID = 'catalog_id', True,  int, 'integer', 'an integer', None, 'the id of the catalog to search'
  GENRE_NAME = 'genre_name', False, str, 'string',  'a string',   None, 'the name of the genres to get'
  GENRE_NAME_HAS_WILDCARDS      = 'genre_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if genre_name isn\'t set, genre_name_has_wildcards is ignored.  if genre_name_has_wildcards is true, % and _ in genre_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if genre_name_has_wildcards is false, % and _ will be treated literally.'
  GENRE_NAME_IS_CASE_SENSITIVE  = 'genre_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if genre_name isn\'t set, genre_name_is_case_sensitive is ignored.  if genre_name_is_case_sensitive is true, letters in genre_name will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  GENRE_NAME_MATCHES_DIACRITICS = 'genre_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if genre_name isn\'t set, genre_name_matches_diacritics is ignored.  if genre_name_matches_diacritics is true, letters in genre_name will be matched exactly; otherwise, diacritics will be stripped out of both the genre_name parameter and genre\'s name, so "a" in the query parameter will match "ä", "à", "å", etc. in the genre name.'
  SORT_ASC    = 'sort_asc',    False, parse_bool, 'boolean', 'a boolean', True, 'if true, the resulting list will be sorted in alphabetical order by genre name.  otherwise, it\'ll be sorted in reverse alphabetical order.'
  PAGE_NUMBER = 'page_number', False, int, 'integer', 'an integer', 1, 'the 1-based number of which page to get; e.g. if you\'re getting 50 results at a time and you want results #51-100, this would be 2.'
  PAGE_SIZE   = 'page_size',   False, parse_page_size, 'integer', 'an integer', 100, 'the size of one page; i.e. the maximum number of results to get.  if this is "all", all results will be returned regardless of what the value of page_number is.'