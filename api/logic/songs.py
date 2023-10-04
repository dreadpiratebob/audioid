from api.dao.load_db_models import get_songs as get_songs_from_db
from api.util.http import HTTPStatusCodes, Response

def get_songs(catalog_id:int, song_name:str, song_year:int, artist:str, album:str, genre:str):
  grievances = []
  
  get_songs_from_db(song_name, song_year, catalog_id, artist_id, album_id, genre_id)

  return Response('to do: get songs', HTTPStatusCodes.HTTP501)