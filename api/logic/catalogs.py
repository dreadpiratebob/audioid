from api.dao.load_db_models import get_catalogs as get_db_catalogs
from api.util.response_list_modifiers import FilterInfo, OrderByCol, PageInfo

def get_catalogs(catalog_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo):
  return get_db_catalogs(catalog_filter, order_by, page_info)