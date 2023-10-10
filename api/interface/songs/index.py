from api.exceptions.http_base import BadRequestException
from api.logic.songs import get_songs
from api.util.audioid import ParamKeys
from api.util.http import HTTPStatusCodes, Response, get_param

def get(environment:dict, path_params:dict, query_params:dict, body):
  grievances = []
  
  catalog_id, error = get_param(ParamKeys.CATALOG_ID.value, query_params, int, 'an int', True, return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  album_id, error = get_param(ParamKeys.ALBUM_ID.value, query_params, int, 'an int', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  album_name, error = get_param(ParamKeys.ALBUM_NAME.value, query_params, str, 'a string', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  if album_id is not None and album_name is not None:
    grievances.append('only one query parameter of "album", "album_id" and "album_name" per request can be set.')
  
  artist_id, error = get_param(ParamKeys.ARTIST_ID.value, query_params, int, 'an int', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  artist_name, error = get_param(ParamKeys.ARTIST_NAME.value, query_params, str, 'a string', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  if artist_id is not None and artist_name is not None:
    grievances.append('only one query parameter of "artist_id" and "artist_name" can be set.')
  
  genre_id, error = get_param(ParamKeys.GENRE.value, query_params, int, 'an int', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  genre_name, error = get_param(ParamKeys.GENRE.value, query_params, str, 'a string', return_error_message=True)
  if error is not None:
    grievances.append(str(error))
  
  if genre_id is not None and genre_name is not None:
    grievances.append('only one query parameter of "genre_id" and "genre_name" can be set.')
  
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
  
  content = get_songs(catalog_id, song_name, song_year, artist_id, artist_name, album_id, album_name, genre_id, genre_name)
  
  return content