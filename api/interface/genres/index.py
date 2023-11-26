from api.exceptions.http_base import BadRequestException
from api.logic.genres import get_genres
from api.models.db_models import Genre
from api.util.audioid.genres import GetGenresQueryParams, GetGenresOrderColumns
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath
from api.util.response_list_modifiers import FilterInfo, OrderByCol, OrderDirection, PageInfo

class Genres:
  def __init__(self, genres:[list, tuple]):
    catalogs_type_error = 'catalogs must be a list or tuple of songs.'
    if not isinstance(genres, (list, tuple)):
      raise TypeError(catalogs_type_error)
    
    for genre in genres:
      if not isinstance(genre, Genre):
        raise TypeError(catalogs_type_error)
    
    self.genres = genres

def get(environment:dict, path_params:dict, query_params:dict, body) -> Response:
  param_val_errors = {param.param_name: param.get_value(query_params) for param in GetGenresQueryParams}
  grievances = []
  for pve in param_val_errors.values():
    if pve[1] is not None:
      grievances.append(str(pve[1]))
  
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  catalog_id = param_val_errors[GetGenresQueryParams.CATALOG_ID.param_name][0]
  
  genre_name                    = param_val_errors[GetGenresQueryParams.GENRE_NAME.param_name][0]
  genre_name_has_wildcards      = param_val_errors[GetGenresQueryParams.GENRE_NAME_HAS_WILDCARDS.param_name][0]
  genre_name_is_case_sensitive  = param_val_errors[GetGenresQueryParams.GENRE_NAME_IS_CASE_SENSITIVE.param_name][0]
  genre_name_matches_diacritics = param_val_errors[GetGenresQueryParams.GENRE_NAME_MATCHES_DIACRITICS.param_name][0]
  genre_filter = FilterInfo(None, genre_name, genre_name_has_wildcards, genre_name_is_case_sensitive, genre_name_matches_diacritics, None)
  
  sort_asc    = param_val_errors[GetGenresQueryParams.SORT_ASC.param_name][0]
  order_by    = [OrderByCol(GetGenresOrderColumns.GENRE_NAME, OrderDirection.ASCENDING if sort_asc else OrderDirection.DESCENDING)]
  page_number = param_val_errors[GetGenresQueryParams.PAGE_NUMBER.param_name][0]
  page_size   = param_val_errors[GetGenresQueryParams.PAGE_SIZE.param_name][0]
  page_info   = None
  if page_size is not None:
    try:
      page_info = PageInfo(page_number, page_size)
    except (ValueError, TypeError) as e:
      raise BadRequestException(str(e))
  
  genres = get_genres(catalog_id, genre_filter, order_by, page_info)
  
  if len(genres) == 0:
    return Response(None, HTTPStatusCodes.HTTP204)
  
  return Response(Genres(genres), HTTPStatusCodes.HTTP200, use_public_fields_only=False)

def get_help() -> AvailablePath:
  return AvailablePath(query_params=tuple(param for param in GetGenresQueryParams), description='this endpoint lists genres in the given catalog, filtered by name if requested and sorted and paginated as requested.')