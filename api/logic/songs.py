from api.dao.load_db_models import \
  get_songs as get_songs_from_db, \
  get_album_by_name, \
  get_artist_by_name, \
  get_genre_by_name
  
from api.util.http import HTTPStatusCodes, Response

def get_songs(catalog_id:int, song_name:str, song_year:int, artist_id:int, artist_name:str, album_id:int, album_name:str, genre_id:int, genre_name:str):
  grievances = []
  
  if artist_name is not None:
    if artist_id is None:
      artist_id = get_artist_by_name(artist_name).get_id()
    else:
      grievances.append('only one of artist_id and artist_name can be set.')
  
  if album_name is not None:
    if album_id is None:
      album_id = get_album_by_name(album_name).get_id()
    else:
      grievances.append('only one of album_id and album_name can be set.')
  
  if genre_name is not None:
    if genre_id is None:
      genre_id = get_genre_by_name(genre_name).get_id()
    else:
      grievances.append('only one of genre_id and genre_name can be set.')
  
  get_songs_from_db(song_name, song_year, catalog_id, artist_id, album_id, genre_id)

  return Response('to do: get songs', HTTPStatusCodes.HTTP501)