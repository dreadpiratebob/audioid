from api.logic.songs import get_song_for_download
from api.util.audioid.songs import GetSongsPathParams
from api.util.http import HTTPStatusCodes, Response

def get(path_params:dict, query_params:dict, body):
  if GetSongsPathParams.SONG_ID.value not in path_params:
    return Response('no song id was given.', HTTPStatusCodes.HTTP500)
  
  song_id = path_params[GetSongsPathParams.SONG_ID.value]
  
  return get_song_for_download(song_id)