from api.dao.flac import get_flac_contents
from api.dao.load_db_models import get_song as get_song_from_db, get_songs as get_songs_from_db
from api.dao.mp3 import get_mp3_contents
from api.models.db_models import FileTypes, Song
from api.util.file_operations import get_file_size_in_bytes
from api.util.response_list_modifiers import FilterInfo, OrderByCol, PageInfo

def get_song(song_id:int, include_artists:bool = True, include_albums:bool = True, include_genres:bool = True, include_catalog_base_path:bool = False):
  return get_song_from_db(song_id, include_artists, include_albums, include_genres, include_catalog_base_path)

def get_song_for_download(song_id:[int, Song], file_type:FileTypes) -> bytes:
  return _get_song_contents(song_id, file_type, False)

def get_song_for_streaming(song_id:[int, Song], file_type:FileTypes) -> bytes:
  return _get_song_contents(song_id, file_type, True)

def _get_song_contents(song:[int, Song], file_type:FileTypes, stream:bool) -> bytes:
  if isinstance(song, int):
    song = get_song(song, False, False, False, True)
    if song is None:
      return None
  
  if file_type == FileTypes.MP3:
    return get_mp3_contents(song, stream)
  elif file_type == FileTypes.FLAC:
    return get_flac_contents(song, stream)
  
  raise ValueError('unsupported file type: %s' % (file_type, ))

def get_song_size_in_bytes(song:[int, Song], file_type:FileTypes) -> int:
  if isinstance(song, int):
    song = get_song(song, False, False, False, True)
    if song is None:
      return None
  
  filename = song.get_full_filename(file_type)
  return get_file_size_in_bytes(filename)

def get_songs(catalog_id:int, song:FilterInfo, song_year:int, artist:FilterInfo, album:FilterInfo, album_artist:FilterInfo, genre:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo):
  return get_songs_from_db(catalog_id, song, song_year, artist, album, album_artist, genre, order_by, page_info)