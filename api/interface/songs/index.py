from api.exceptions.http_base import BadRequestException
from api.logic.songs import get_songs
from api.util.audioid import GetSongsQueryParams
from api.util.http_path import AvailablePath

def get(environment:dict, path_params:dict, query_params:dict, body):
  param_val_errors = {param.param_name: param.get_value(query_params, return_error_message=False) for param in GetSongsQueryParams}
  params = {param_name: param_val_errors[param_name][0] for param_name in param_val_errors}
  grievances = [pve[1] for pve in param_val_errors.values()]
  
  album_id = params[GetSongsQueryParams.ALBUM_ID.param_name]
  album_name = params[GetSongsQueryParams.ALBUM_NAME.param_name]
  album_name_is_an_exact_match = params[GetSongsQueryParams.ALBUM_NAME_IS_AN_EXACT_MATCH.param_name]
  if album_id is not None and album_name is not None:
    grievances.append('only one query parameter of "album_id" and "album_name" per request can be set.')

  album_artist_id = params[GetSongsQueryParams.ALBUM_ARTIST_ID.param_name]
  album_artist_name = params[GetSongsQueryParams.ALBUM_ARTIST_NAME.param_name]
  album_artist_name_is_an_exact_match = params[GetSongsQueryParams.ALBUM_ARTIST_NAME_IS_AN_EXACT_MATCH.param_name]
  if album_artist_id is not None and album_artist_name is not None:
    grievances.append('only one query parameter of "album_artist_id" and "album_artist_name" can be set.')
  
  artist_id = params[GetSongsQueryParams.ARTIST_ID.param_name]
  artist_name = params[GetSongsQueryParams.ARTIST_NAME.param_name]
  artist_name_is_an_exact_match = params[GetSongsQueryParams.ARTIST_NAME_IS_AN_EXACT_MATCH.param_name]
  if artist_id is not None and artist_name is not None:
    grievances.append('only one query parameter of "artist_id" and "artist_name" can be set.')
  
  genre_id = params[GetSongsQueryParams.GENRE_ID.param_name]
  genre_name = params[GetSongsQueryParams.GENRE_NAME.param_name]
  genre_name_is_an_exact_match = params[GetSongsQueryParams.GENRE_NAME_IS_AN_EXACT_MATCH.param_name]
  if genre_id is not None and genre_name is not None:
    grievances.append('only one query parameter of "genre_id" and "genre_name" can be set.')
  
  catalog_id = params[GetSongsQueryParams.CATALOG_ID.param_name]
  if not isinstance(catalog_id, int) or catalog_id < 0:
    grievances.append('a catalog id must be a nonnegative int.')
  
  song_name = params[GetSongsQueryParams.SONG_NAME.param_name]
  song_year = params[GetSongsQueryParams.SONG_YEAR.param_name]
  
  if len(grievances) > 0:
    raise BadRequestException('\n'.join(grievances))
  
  return get_songs(catalog_id, song_name, song_year,
                   artist_id, artist_name, artist_name_is_an_exact_match,
                   album_id, album_name, album_name_is_an_exact_match,
                   album_artist_id, album_artist_name, album_artist_name_is_an_exact_match,
                   genre_id, genre_name, genre_name_is_an_exact_match)

def get_help():
  return AvailablePath(query_params=(param for param in GetSongsQueryParams), description='this endpoint lists available songs, filtered and sorted as requested.  [note: sorting hasn\'t been implemented yet.]  no auth necessary.')