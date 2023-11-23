from api.dao.load_db_models import get_genres as get_db_genres
from api.util.response_list_modifiers import FilterInfo, OrderByCol, PageInfo

def get_genres(catalog_id:int, genre_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo):
  return get_db_genres(catalog_id, genre_filter, order_by, page_info)