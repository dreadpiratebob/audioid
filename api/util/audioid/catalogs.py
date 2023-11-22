from api.util.functions import parse_bool
from api.util.http import QueryParam
from api.util.response_list_modifiers import OrderByCol, OrderColName, OrderDirection, parse_page_size

class GetCatalogsOrderColumns(OrderColName):
  CATALOG_NAME = 'catalog_name', 'the catalog\'s name'

get_catalogs_order_columns_by_column_name = {col.column_name: col for col in GetCatalogsOrderColumns}
default_get_catalogs_order_by = tuple \
(
  [
    OrderByCol(GetCatalogsOrderColumns.CATALOG_NAME, OrderDirection.ASCENDING)
  ]
)

class GetCatalogsQueryParams(QueryParam):
  CATALOG_NAME = 'catalog_name', False, str, 'string', 'a string', None, 'the name of the catalogs to get'
  CATALOG_NAME_HAS_WILDCARDS      = 'catalog_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if catalog_name isn\'t set, catalog_name_has_wildcards is ignored.  if catalog_name_has_wildcards is true, % and _ in catalog_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if catalog_name_has_wildcards is false, % and _ will be treated literally.'
  CATALOG_NAME_IS_CASE_SENSITIVE  = 'catalog_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if catalog_name isn\'t set, catalog_name_is_case_sensitive is ignored.  if catalog_name_is_case_sensitive is true, letters in catalog_name will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  CATALOG_NAME_MATCHES_DIACRITICS = 'catalog_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if catalog_name isn\'t set, catalog_name_matches_diacritics is ignored.  if catalog_name_matches_diacritics is true, letters in catalog_name will be matched exactly; otherwise, diacritics will be stripped out of both the catalog_name parameter and catalog\'s name, so "a" in the query parameter will match "ä", "à", "å", etc. in the catalog name.'
  SORT_ASC    = 'sort_asc',    False, parse_bool, 'boolean', 'a boolean', True, 'if true, the resulting list will be sorted in alphabetical order by catalog name.  otherwise, it\'ll be sorted in reverse alphabetical order.'
  PAGE_NUMBER = 'page_number', False, int, 'integer', 'an integer', 1, 'the 1-based number of which page to get; e.g. if you\'re getting 50 results at a time and you want results #51-100, this would be 2.'
  PAGE_SIZE   = 'page_size',   False, parse_page_size, 'integer', 'an integer', 100, 'the size of one page; i.e. the maximum number of results to get.  if this is "all", all results will be returned regardless of what the value of page_number is.'