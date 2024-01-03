from api.exceptions.http_base import BadRequestException
from api.logic.songs import get_song
from api.util.audioid.songs import GetSongPathParams, GetSongQueryParams
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath

def get(environment:dict, path_params:dict, query_params:dict, body) -> Response:
  song_id, song_id_error = GetSongPathParams.SONG_ID.get_value(path_params, True)
  if song_id_error is not None:
    return Response(str(song_id_error), HTTPStatusCodes.HTTP400)
  
  parsed_query_params = {param: param.get_value(query_params, True) for param in GetSongQueryParams}
  grievances = []
  for pqp in parsed_query_params:
    if parsed_query_params[pqp][1] is not None:
      grievances.append(str(parsed_query_params[pqp][1]))
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  include_artists = parsed_query_params[GetSongQueryParams.INCLUDE_ARTISTS]
  include_albums  = parsed_query_params[GetSongQueryParams.INCLUDE_ALBUMS]
  include_genres  = parsed_query_params[GetSongQueryParams.INCLUDE_GENRES]
  
  song = get_song(song_id, include_artists, include_albums, include_genres)
  
  if song is None:
    return Response(None, HTTPStatusCodes.HTTP404)
  
  return Response(song, HTTPStatusCodes.HTTP200, use_public_fields_only=False)

def get_help():
  return AvailablePath(query_params=tuple(param for param in GetSongQueryParams), path_params=tuple(param for param in GetSongPathParams), description='this endpoint gets information about a particular song.')