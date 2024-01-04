from api.logic.songs import get_song_for_download
from api.util.audioid.songs import DownloadSongPathParams
from api.util.http import HTTPStatusCodes, Response
from api.util.http_path import AvailablePath

def get(environment:dict, path_params:dict, query_params:dict, body) -> Response:
  song_id, song_id_error = DownloadSongPathParams.SONG_ID.get_value(path_params, True)
  if song_id_error is not None:
    return Response(str(song_id_error), HTTPStatusCodes.HTTP400)
  
  content = get_song_for_download(song_id)
  
  return Response(content, HTTPStatusCodes.HTTP200)

def get_help():
  return AvailablePath(path_params=tuple(param for param in DownloadSongPathParams), description='this endpoint provides the content of a particular song.')