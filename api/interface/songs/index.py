from api.exceptions.http_base import BadRequestException
from api.logic.songs import get_songs
from api.util.audioid import ParamKeys
from api.util.http import HTTPStatusCodes, Response, get_param

def get(environment:dict, path_params:dict, query_params:dict, body):
  grievances = []
  
  catalog_id, error = get_param(ParamKeys.CATALOG_ID.value, query_params, int, 'an int', True, return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  album, error = get_param(ParamKeys.ALBUM.value, query_params, str, 'a string', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  artist, error = get_param(ParamKeys.ARTIST.value, query_params, str, 'a string', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  genre, error = get_param(ParamKeys.GENRE.value, query_params, int, 'an int', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  song_name, error = get_param(ParamKeys.SONG_NAME.value, query_params, str, 'a string', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  song_year, error = get_param(ParamKeys.SONG_YEAR.value, query_params, int, 'an int', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  if not isinstance(catalog_id, int) or catalog_id < 0:
    grievances.append('a catalog id must be a nonnegative int.')
  
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  content = get_songs(catalog_id, song_name, song_year, artist, album, genre)
  
  return content