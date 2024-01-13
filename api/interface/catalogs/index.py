from api.exceptions.http_base import BadRequestException
from api.logic.catalogs import get_catalogs
from api.models.db_models import Catalog
from api.util.audioid.catalogs import GetCatalogsQueryParams, GetCatalogsOrderColumns
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath
from api.util.response_list_modifiers import FilterInfo, OrderByCol, OrderDirection, PageInfo

class Catalogs:
  def __init__(self, catalogs: [list, tuple]):
    catalogs_type_error = 'catalogs must be a list or tuple of catalogs.'
    if not isinstance(catalogs, (list, tuple)):
      raise TypeError(catalogs_type_error)
    
    for catalog in catalogs:
      if not isinstance(catalog, Catalog):
        raise TypeError(catalogs_type_error)
    
    self.catalogs = catalogs

def get(environment:dict, headers:dict, path_params:dict, query_params:dict, body) -> Response:
  param_val_errors = {param.param_name: param.get_value(query_params) for param in GetCatalogsQueryParams}
  grievances = []
  for pve in param_val_errors.values():
    if pve[1] is not None:
      grievances.append(str(pve[1]))
  
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  catalog_name                    = param_val_errors[GetCatalogsQueryParams.CATALOG_NAME.param_name][0]
  catalog_name_has_wildcards      = param_val_errors[GetCatalogsQueryParams.CATALOG_NAME_HAS_WILDCARDS.param_name][0]
  catalog_name_is_case_sensitive  = param_val_errors[GetCatalogsQueryParams.CATALOG_NAME_IS_CASE_SENSITIVE.param_name][0]
  catalog_name_matches_diacritics = param_val_errors[GetCatalogsQueryParams.CATALOG_NAME_MATCHES_DIACRITICS.param_name][0]
  catalog_filter = FilterInfo(None, catalog_name, catalog_name_has_wildcards, catalog_name_is_case_sensitive, catalog_name_matches_diacritics, None)
  
  sort_asc    = param_val_errors[GetCatalogsQueryParams.SORT_ASC.param_name][0]
  order_by    = [OrderByCol(GetCatalogsOrderColumns.CATALOG_NAME, OrderDirection.ASCENDING if sort_asc else OrderDirection.DESCENDING)]
  page_number = param_val_errors[GetCatalogsQueryParams.PAGE_NUMBER.param_name][0]
  page_size   = param_val_errors[GetCatalogsQueryParams.PAGE_SIZE.param_name][0]
  page_info   = None
  if page_size is not None:
    try:
      page_info = PageInfo(page_number, page_size)
    except (ValueError, TypeError) as e:
      raise BadRequestException(str(e))
  
  catalogs = get_catalogs(catalog_filter, order_by, page_info)
  
  if len(catalogs) == 0:
    return Response(None, HTTPStatusCodes.HTTP204)
  
  return Response(Catalogs(catalogs), HTTPStatusCodes.HTTP200, use_public_fields_only=False)

def get_help() -> AvailablePath:
  return AvailablePath(query_params=tuple(param for param in GetCatalogsQueryParams), description='this endpoint lists available catalogs, filtered by name if requested and sorted and paginated as requested.')