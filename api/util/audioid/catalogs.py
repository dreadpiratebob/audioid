from api.util.functions import parse_bool
from api.util.http import QueryParam
from api.util.response_list_modifiers import OrderByCol, OrderColName, OrderDirection, get_order_parser, parse_page_size

class GetCatalogsOrderColumns(OrderColName):
  CATALOG_NAME = 'catalog_name', 'the catalog\'s name'

get_catalogs_order_columns_by_column_name = {col.column_name: col for col in GetCatalogsOrderColumns}
default_get_songs_order_by = \
[
  OrderByCol(GetCatalogsOrderColumns.CATALOG_NAME, OrderDirection.ASCENDING)
]

class GetCatalogsQueryParams(QueryParam):
  CATALOG_NAME = 'catalog_name', False, str, 'string', 'a string', None, 'the name of the catalogs to get'
  ORDER_BY     = 'order_by',     False, get_order_parser(GetCatalogsOrderColumns, get_catalogs_order_columns_by_column_name), 'a comma-separated list of song-columns/direction pairs', 'a comma-separated list of song-columns/direction pairs', default_get_songs_order_by, 'each song column name must be one of %s; each direction must be "ascending" or "descending".  (each of those is case-insensitive.)' % (', '.join([col.column_name for col in GetCatalogsOrderColumns]),)
  PAGE_NUMBER  = 'page_number',  False, int, 'integer', 'an integer', 1, 'the 1-based number of which page to get; e.g. if you\'re getting 50 results at a time and you want results #51-100, this would be 2.'
  PAGE_SIZE    = 'page_size',    False, parse_page_size, 'integer', 'an integer', 100, 'the size of one page; i.e. the maximum number of results to get.  if this is "all", all results will be returned regardless of what the value of page_number is.'