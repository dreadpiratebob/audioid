from models.db_models import Album
from models.db_models import Artist
from models.db_models import ArtistJoin
from models.db_models import Genre
from models.db_models import Song
from models.db_models import SongAlbum
from models.db_models import SongGenre

from util.logger import get_logger

def build_song_from_mp3(mp3, catalog, artist_splitters = [' feat ', ' feat. ', ' featuring ', ' remixed by ', ' covered by ', ', ', ' vs ', ' vs. ', ' & ']):
  song_name = mp3.title
  if song_name is None:
    song_name = mp3.filename
    while '/' in song_name:
      song_name = song_name[song_name.index('/')+1:]
  else:
    song_name = str(song_name)
  
  song_year = mp3.year
  if song_year is not None:
    song_year = int(song_year)
  
  song_fn = mp3.filename[len(catalog.base_path):]
  
  get_logger().debug('rel path: %s' % song_fn)
  song = Song(None, song_name, song_year, song_fn, None, int(mp3.date_modified), catalog)
  
  if mp3.artist is not None and mp3.artist != '':
    song.artists = get_artist_joins(song, str(mp3.artist), artist_splitters)
  
  if mp3.album is not None and mp3.album != '':
    album_artist = None
    if mp3.album_artist is not None:
      album_artist = Artist(None, mp3.album_artist)
    album = Album(None, mp3.album, album_artist)
    album_join = SongAlbum(song, album, None if mp3.track is None else int(mp3.track))
    song.albums = [album_join]
  
  if mp3.genre is not None and mp3.genre != '':
    genre = Genre(None, mp3.genre)
    song_genre = SongGenre(song, genre)
    song.genres = [song_genre]
  
  return song

def get_artist_joins(song, artist_str, artist_splitters):
  if artist_str is None:
    return None
  
  result = []
  beginning = 0
  end = len(artist_str)

  i = 0
  while i < end:
    for splitter in artist_splitters:
      if i + len(splitter) > end:
        continue

      chunk = artist_str[i:i + len(splitter)]
      if chunk == splitter:
        artist = Artist(None, artist_str[beginning:i])
        artist_join = ArtistJoin(song, artist, len(result), splitter)
        result.append(artist_join)
        
        i += len(splitter) - 1
        beginning = i + 1
        
        break
    
    i += 1
  
  artist = Artist(None, artist_str[beginning:])
  artist_join = ArtistJoin(song, artist, len(result))
  result.append(artist_join)
  
  return result