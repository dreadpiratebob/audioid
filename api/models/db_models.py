from api.exceptions.song_data import\
  InvalidArtistDataException,\
  InvalidCatalogDataException,\
  InvalidSongDataException
from api.util.functions import get_search_text_from_raw_text, is_iterable

class Catalog:
  def __init__(self, id:int, name:str, base_path:str):
    grievances = []
    
    if id is not None and not isinstance(id, int):
      grievances.append('an id must be an int.')
    
    if not isinstance(name, str):
      grievances.append('a name must be a str.')
    
    if base_path is not None and not isinstance(base_path, str):
      grievances.append('a base path must be a str.')
    
    if len(grievances) > 0:
      raise InvalidCatalogDataException('\n'.join(grievances))
    
    self._id = id
    self._name = name
    self._base_path = base_path
  
  def __eq__(self, other):
    return isinstance(other, Catalog) and \
      self._id == other._id and \
      self._name == other._name and \
      self._base_path == other._base_path
  
  def __hash__(self):
    return (((hash(self._id)*397) ^ hash(self._name))*397) ^ hash(self._base_path)
  
  def __str__(self):
    return self.get_name() + ' (' + self.get_base_path() + ')'
  
  def get_id(self):
    return self._id
  
  def get_name(self):
    return self._name
  
  def set_name(self, name:str):
    if not isinstance(name, str):
      raise ValueError('a name must be a str.')
    
    self._name = name
  
  def get_base_path(self):
    return self._base_path
  
  def set_base_path(self, base_path:str):
    if not isinstance(base_path, str):
      raise ValueError('a base path must be a str.')
    
    self._base_path = base_path

def song_album_key(s_al):
  return s_al.get_track_number()

def song_artist_key(s_ar):
  return s_ar.get_list_order()

class Song:
  def __init__(self, id:int, title:str, lcase_title:str, no_diacritic_title:str, lcase_no_diacritic_title:str, year:int, duration:float, filename:str, file_last_modified:int, catalog, genres = None,
               songs_albums = None, songs_artists = None, song_similarities_from_song2 = None, song_similarities_from_song1 = None,
               last_scanned:int = None):
    grievances = []
    
    if id is not None and not isinstance(id, int):
      grievances.append('an id must be an int.')
    
    if not isinstance(title, str):
      grievances.append('a title must be a str.')
    
    if lcase_title is not None and not isinstance(lcase_title, str):
      grievances.append('a title must be a str.')
    
    if no_diacritic_title is not None and not isinstance(no_diacritic_title, str):
      grievances.append('a title must be a str.')
    
    if lcase_no_diacritic_title is not None and not isinstance(lcase_no_diacritic_title, str):
      grievances.append('a title must be a str.')
    
    if year is not None and not isinstance(year, int):
      grievances.append('a year must be an int.')
    
    if not isinstance(duration, float):
      grievances.append('a duration must be a float.')
    
    if filename is not None and not isinstance(filename, str):
      grievances.append('a filename must be a str.')
    
    if last_scanned is not None and not isinstance(last_scanned, int):
      grievances.append('a last_scanned must be an int.')
    
    if file_last_modified is not None and not isinstance(file_last_modified, int):
      grievances.append('a last_modified timestamp must be an int.')
    
    if genres is None:
      genres = list()
    elif not is_iterable(genres):
      grievances.append('a collection of genres must be iterable.')
    
    if songs_artists is None:
      songs_artists = list()
    elif not is_iterable(songs_artists):
      grievances.append('a collection of songs_artists must be iterable.')
    
    if songs_albums is None:
      songs_albums = list()
    elif not is_iterable(songs_albums):
      grievances.append('a collection of songs_albums must be iterable.')
    
    if song_similarities_from_song1 is None:
      song_similarities_from_song1 = list()
    
    if song_similarities_from_song2 is None:
      song_similarities_from_song2 = list()
    
    if len(grievances) > 0:
      raise InvalidSongDataException('\n'.join(grievances))
    
    songs_albums = list(songs_albums)
    songs_albums.sort(key=song_album_key)
    
    songs_artists = list(songs_artists)
    songs_artists.sort(key=song_artist_key)
    
    if lcase_title is None or no_diacritic_title is None or lcase_no_diacritic_title is None:
      _lcase, _no_diacritic, _lcase_no_diacritic = get_search_text_from_raw_text(title)
      if lcase_title is None:
        lcase_title = _lcase
      if no_diacritic_title is None:
        no_diacritic_title = _no_diacritic
      if lcase_no_diacritic_title is None:
        lcase_no_diacritic_title = _lcase_no_diacritic
    
    self._id = id
    self._title = title
    self._lcase_title = lcase_title
    self._no_diacritic_title = no_diacritic_title
    self._lcase_no_diacritic_title = lcase_no_diacritic_title
    self._year = year
    self._duration = duration
    self._filename = filename
    self._catalog = catalog
    self._last_scanned = last_scanned
    self._file_last_modified = file_last_modified
    self._genres = list(genres)
    self._songs_albums = songs_albums
    self._songs_artists = songs_artists
    self._song_similarities_from_song2 = list(song_similarities_from_song2)
    self._song_similarities_from_song1 = list(song_similarities_from_song1)
  
  def __str__(self):
    return '"' + self.get_title() + '" by ' + ''.join([s_a.get_artist().get_name() + ('' if s_a.get_conjunction() is None else s_a.get_conjunction()) for s_a in self.get_songs_artists()])
  
  def get_id(self):
    return self._id
  
  def set_id(self, id:int):
    if not isinstance(id, int):
      raise ValueError('an id must be an int.')
    
    self._id = id
  
  def get_title(self):
    return self._title
  
  def set_title(self, title:str):
    if not isinstance(title, str):
      raise ValueError('a song title must be a str.')
    
    self._title = title
    self._lcase_title, self._no_diacritic_title, self._lcase_no_diacritic_title = get_search_text_from_raw_text(title)
  
  def get_lcase_title(self):
    return self._lcase_title
  
  def get_no_diacritic_title(self):
    return self._no_diacritic_title
  
  def get_lcase_no_diacritic_title(self):
    return self._lcase_no_diacritic_title
  
  def get_year(self):
    return self._year
  
  def set_year(self, year:int):
    if not isinstance(year, int):
      raise ValueError('a year must be an int.')
    
    self._year = year
  
  def get_duration(self):
    return self._duration
  
  def set_duration(self, duration:float):
    if not isinstance(duration, float):
      raise ValueError('a duration must be a float.')
    
    self._duration = duration
  
  def get_filename(self):
    return self._filename
  
  def set_filename(self, filename:str):
    if not isinstance(filename, str):
      raise ValueError('a filename must be a str.')
    
    self._filename = filename
  
  def get_full_filename(self):
    return self.get_catalog().get_base_path() + self.get_filename()
  
  def get_last_scanned(self):
    return self._last_scanned
  
  def set_last_scanned(self, last_scanned:int):
    if not isinstance(last_scanned, int):
      raise ValueError('a last scanned timestamp must be an int.')
    
    self._last_scanned = last_scanned
  
  def get_file_last_modified(self):
    return self._file_last_modified
  
  def set_file_last_modified(self, file_last_modified:int):
    if not isinstance(file_last_modified, int):
      raise ValueError('a last modified timestamp must be an int.')
  
    self._file_last_modified = file_last_modified
  
  def get_catalog(self):
    return self._catalog
  
  def set_catalog(self, catalog):
    self._catalog = catalog
  
  def get_genres(self):
    return self._genres
  
  def set_genres(self, genres):
    if not is_iterable(genres):
      raise TypeError('a collection of genres must be iterable.')
    
    self._genres = set(genres)
  
  def get_songs_albums(self):
    return self._songs_albums
  
  def set_songs_albums(self, songs_albums):
    if not is_iterable(songs_albums):
      raise TypeError('songs_albums must be iterable.')
    
    songs_albums = list(songs_albums)
    songs_albums.sort(key=song_album_key)
    
    self._songs_albums = songs_albums
  
  def get_songs_artists(self):
    return self._songs_artists
  
  def set_songs_artists(self, songs_artists):
    if not is_iterable(songs_artists):
      raise TypeError('songs_artists must be iterable.')
    
    songs_artists = list(songs_artists)
    songs_artists.sort(key=song_artist_key)
    
    self._songs_artists = songs_artists
  
  def get_song_similarities_from_song2(self):
    return self._song_similarities_from_song2
  
  def set_song_similarities_from_song2(self, song_similarities_from_song2):
    self._song_similarities_from_song2 = song_similarities_from_song2
  
  def get_song_similarities_from_song1(self):
    return self._song_similarities_from_song1
  
  def set_song_similarities_from_song1(self, song_similarities_from_song1):
    self._song_similarities_from_song1 = song_similarities_from_song1

class Artist:
  def __init__(self, id:int, name:str, songs_artists = None, albums = None):
    grievances = []
    
    if id is not None and not isinstance(id, int):
      grievances.append('an id must be an int.')
    
    if not isinstance(name, str):
      grievances.append('a name must be a str.')
    
    if len(grievances) > 0:
      raise InvalidArtistDataException('\n'.join(grievances))
    
    self._id = id
    self._songs_artists = songs_artists
    self._albums = albums
    self._name = name
  
  def __str__(self):
    return self._name
  
  def get_id(self):
    return self._id
  
  def get_name(self):
    return self._name
  
  def set_name(self, name:str):
    if not isinstance(name, str):
      raise ValueError('a name must be a str.')
  
    self._name = name
  
  def get_songs_artists(self):
    return self._songs_artists
  
  def set_songs_artists(self, songs_artists_from_artist_id):
    self._songs_artists = songs_artists_from_artist_id
  
  def get_albums_from_album_artist(self):
    return self._albums
  
  def set_albums_from_album_artist(self, albums_from_album_artist):
    self._albums = albums_from_album_artist

class SongArtist:
  def __init__(self, song, artist, list_order:int, conjunction:str = ''):
    grievances = []
    
    if not isinstance(list_order, int):
      grievances.append('a list order must be an int.')
    
    if not isinstance(conjunction, str):
      grievances.append('a conjunction must be a str.')
    
    self._list_order = list_order
    self._song = song
    self._artist = artist
    self._conjunction = conjunction
  
  def get_song(self):
    return self._song
  
  def set_song(self, song):
    self._song = song
  
  def get_artist(self):
    return self._artist
  
  def set_artist(self, artist):
    self._artist = artist
  
  def get_list_order(self):
    return self._list_order
  
  def set_list_order(self, list_order:int):
    if not isinstance(list_order, int):
      raise ValueError('a list order must be an int.')
  
    self._list_order = list_order

  def get_conjunction(self):
    return self._conjunction
  
  def set_conjunction(self, conjunction:str):
    if not isinstance(conjunction, str):
      raise ValueError('a conjunction must be a str.')
    
    self._conjunction = conjunction

class Album:
  def __init__(self, id:int, name:str, lcase_name:str, no_diacritic_name:str, lcase_no_diacritic_name:str, album_artist:Artist, songs_albums = None):
    grievances = []
    
    if id is not None and not isinstance(id, int):
      grievances.append('an id must be an int.')
    
    if not isinstance(name, str):
      grievances.append('a name must be a str.')
    
    if lcase_name is not None and not isinstance(lcase_name, str):
      grievances.append('a name must be a str.')
    
    if no_diacritic_name is not None and not isinstance(no_diacritic_name, str):
      grievances.append('a name must be a str.')
    
    if lcase_no_diacritic_name is not None and not isinstance(lcase_no_diacritic_name, str):
      grievances.append('a name must be a str.')
    
    if album_artist is not None and not isinstance(album_artist, Artist):
      grievances.append('an album artist must be an Artist.')
    
    if len(grievances) > 0:
      raise InvalidArtistDataException('\n'.join(grievances))
    
    if songs_albums is None:
      songs_albums = list()
    
    self._id = id
    self._name = name
    self._lcase_name = lcase_name
    self._no_diacritic_name = no_diacritic_name
    self._lcase_no_diacritic_name = lcase_no_diacritic_name
    self._album_artist = album_artist
    self._songs_albums = songs_albums
    
    if lcase_name is None or no_diacritic_name is not None or lcase_no_diacritic_name is not None:
      self.set_name(name)
  
  def __str__(self):
    return self._name + ' by ' + self._album_artist.get_name() + ':\n' + \
      '\n'.join('  ' + str(s_a.get_track_number()) + '. ' + str(s_a.get_song()) for s_a in self._songs_albums)
  
  def get_id(self):
    return self._id
  
  def get_name(self):
    return self._name
  
  def set_name(self, name:str):
    if not isinstance(name, str):
      raise ValueError('a name must be a str.')
    
    self._name = name
    
    self._lcase_name, self._no_diacritic_name, self._lcase_no_diacritic_name = get_search_text_from_raw_text(name)
  
  def get_lcase_name(self):
    return self._lcase_name
  
  def get_no_diacritic_name(self):
    return self._no_diacritic_name
  
  def get_lcase_no_diacritic_name(self):
    return self._name
  
  def get_album_artist(self):
    return self._album_artist
  
  def set_album_artist(self, album_artist:Artist):
    if not isinstance(album_artist, Artist):
      raise TypeError('an album artist must be an Artist.')
    
    self._album_artist = album_artist
  
  def get_songs_albums(self):
    return self._songs_albums
  
  def set_songs_albums(self, songs_albums):
    self._songs_albums = songs_albums

class SongAlbum:
  def __init__(self, song:Song, album:Album, track_number:int):
    grievances = []
    
    if not isinstance(song, Song):
      grievances.append('a song must be a Song.')
    
    if not isinstance(album, Album):
      grievances.append('an album must be an Album.')
    
    if not isinstance(track_number, int):
      grievances.append('a track number must be an int.')
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    self._song = song
    self._album = album
    self._track_number = track_number
  
  def get_song_from_song_id(self):
    return self._song
  
  def set_song(self, song:Song):
    if not isinstance(song, Song):
      raise TypeError('a song must be a Song.')
    
    self._song = song
  
  def get_album(self):
    return self._album
  
  def set_album(self, album:Album):
    if not isinstance(album, Album):
      raise TypeError('an album must be an Album.')
    
    self._album = album
  
  def get_track_number(self):
    return self._track_number
  
  def set_track_number(self, track_number:int):
    if not isinstance(track_number, int):
      raise ValueError('a track number must be an int.')
    
    self._track_number = track_number

class Genre:
  def __init__(self, id:int, name:str):
    grievances = []
    
    if id is not None and not isinstance(id, int):
      grievances.append('an id must be an int.')
    
    if not isinstance(name, str):
      grievances.append('a name must be a str.')
    
    self._id = id
    self._name = name
  
  def __str__(self):
    return self._name
  
  def get_id(self):
    return self._id
  
  def get_name(self):
    return self._name
  
  def set_name(self, name:str):
    if not isinstance(name, str):
      raise ValueError('a(n) name must be a(n) str.')
    
    self._name = name

class SongGenre:
  def __init__(self, song:Song, genre:Genre):
    grievances = []
    
    if not isinstance(song, Song):
      grievances.append('a song must be a Song.')
    
    if not isinstance(genre, Genre):
      grievances.append('a genre must be a Genre.')
    
    if len(grievances) > 0:
      raise TypeError(grievances)
    
    self._song = song
    self._genre = genre
  
  def get_song(self):
    return self._song
  
  def set_song(self, song):
    self._song = song
  
  def get_genre(self):
    return self._genre
  
  def set_genre(self, genre):
    self._genre = genre