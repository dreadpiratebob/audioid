from api.util.http import HTTPStatusCodes, Response

def get(path_params:dict, query_params:dict, body):
  return Response('to do: get songs', HTTPStatusCodes.HTTP501)