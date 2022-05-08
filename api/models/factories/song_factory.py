from models.db_models import Album
from models.db_models import Artist
from models.db_models import ArtistJoin
from models.db_models import Genre
from models.db_models import Song
from models.db_models import SongAlbum
from models.db_models import SongGenre

def build_song_from_mp3(mp3, catalog, artist_splitters, load_ids = False):
  song = Song(None, mp3.title, mp3.year, mp3.filename, catalog)
  
  if mp3.artist is not None:
    # TO DO
    song.artists = []
  
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

def load_ids(song):
  # TO DO
  pass