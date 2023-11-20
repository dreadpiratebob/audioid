from api.util.audioid.catalogs import GetCatalogsQueryParams
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath

def get(environment:dict, path_params:dict, query_params:dict, body):
  return Response(None, HTTPStatusCodes.HTTP501)

def get_help() -> AvailablePath:
  return AvailablePath(query_params=tuple(param for param in GetCatalogsQueryParams), description='this endpoint lists available catalogs, filtered by name if requested and sorted and paginated as requested.')