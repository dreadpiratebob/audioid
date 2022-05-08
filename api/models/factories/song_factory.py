from models.db_models import Album
from models.db_models import Artist
from models.db_models import ArtistJoin
from models.db_models import Genre
from models.db_models import Song
from models.db_models import SongAlbum
from models.db_models import SongGenre

from util.logger import get_logger

def build_song_from_mp3(mp3, catalog, artist_splitters = [' feat ', ' feat. ', ' featuring ', ', ', ' vs ', ' vs. '], load_ids = False):
  song = Song(None, mp3.title, mp3.year, mp3.filename, None, mp3.date_modified, catalog)
  
  if mp3.artist is not None:
    song.artists = get_artist_joins(song, mp3.artist, artist_splitters)
    for artist_join in song.artists:
      get_logger().debug(str(artist_join))
  
  if mp3.album is not None:
    album_artist = None
    if mp3.album_artist is not None:
      album_artist = Artist(None, mp3.album_artist)
    album = Album(None, mp3.album, album_artist)
    album_join = SongAlbum(song, album, mp3.track)
    song.albums = [album_join]
  
  if mp3.genre is not None:
    genre = Genre(None, mp3.genre)
    song_genre = SongGenre(song, genre)
    song.genres = [song_genre]
  
  if load_ids:
    load_ids(song)
  
  return song

def get_artist_joins(song, artist_str, artist_splitters):
  if artist_str is None:
    return None
  
  result = []
  logger = get_logger()
  logger.debug('attempting to read artist data:')
  logger.debug('artist: %s' % artist_str)
  logger.debug('splitters: %s' % str(artist_splitters))
  
  beginning = 0
  end = len(artist_str)
  
  i = 0
  while i < end:
    for splitter in artist_splitters:
      logger.debug('at position %s in "%s" looking for splitter "%s"...' %(str(i), artist_str, splitter))
      if i + len(splitter) < end and artist_str[i:i + len(splitter)] == splitter:
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

def load_ids(song):
  # TO DO
  pass