from api.models.db_models import \
  Album, \
  Artist, \
  SongArtist, \
  Catalog, \
  Genre, \
  Song, \
  SongAlbum

from api.util.logger import get_logger

def build_song_from_mp3(mp3, catalog:Catalog, artist_splitters = None) -> Song:
  if artist_splitters is None:
    artist_splitters = [' feat ', ' feat. ', ' featuring ', ' remixed by ', ' covered by ', ', ', ' vs ', ' vs. ', ' & ']
  
  song_name = mp3.title
  if song_name is None:
    song_name = mp3.filename[mp3.filename.rfind('/')+1:]
  else:
    song_name = str(song_name)
  
  song_year = mp3.year
  if song_year is not None:
    song_year = int(song_year)
  
  song_fn = catalog.get_song_filename_from_full_filename(mp3.filename)
  
  song_duration = mp3.duration
  
  get_logger().debug('rel path: %s' % song_fn)
  song = Song(None, song_name, None, None, None, song_year, song_duration, song_fn, int(mp3.date_modified), catalog, None, None, None, None, None)
  
  if mp3.artist is not None and mp3.artist != '':
    song.set_songs_artists(get_artist_joins(song, str(mp3.artist), artist_splitters))
  
  if mp3.album is not None and mp3.album != '':
    album_artist = None
    if mp3.album_artist is not None:
      album_artist = Artist(None, mp3.album_artist, None, None, None)
    album = Album(None, mp3.album, None, None, None, album_artist)
    album_join = SongAlbum(song, album, None if mp3.track is None else int(mp3.track))
    song.set_songs_albums([album_join])
  
  if mp3.genre is not None and mp3.genre != '':
    genre = Genre(None, mp3.genre, None, None, None)
    song.set_genres({genre})
  
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
      if chunk != splitter:
        continue
      
      artist = Artist(None, artist_str[beginning:i], None, None, None)
      artist_join = SongArtist(song, artist, len(result), splitter)
      result.append(artist_join)
      
      i += len(splitter) - 1
      beginning = i + 1
      
      break
    
    i += 1
  
  artist = Artist(None, artist_str[beginning:], None, None, None)
  artist_join = SongArtist(song, artist, len(result))
  result.append(artist_join)
  
  return result