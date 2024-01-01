from api.exceptions.song_data import\
  InvalidArtistDataException,\
  InvalidCatalogDataException,\
  InvalidSongDataException
from api.exceptions.http_base import NotImplementedException
from api.util.file_operations import AudioFileTypes, get_file_size_in_bytes
from api.util.functions import get_search_text_from_raw_text, get_type_name, is_iterable

import os

class DBModel:
  def __eq__(self, other:any) -> bool:
    if not isinstance(other, type(self)):
      return False
    
    return self._recursive_equals(other)
  
  def __ne__(self, other:any) -> bool:
    if not isinstance(other, type(self)):
      return True
    
    return not self._recursive_equals(other)
  
  def _recursive_equals(self, other:any, seen_objects:list = None) -> bool:
    if seen_objects is None:
      seen_objects = []
    
    other_id = other
    if isinstance(other, DBModel):
      other_id = other._get_unique_id()
    
    if other_id in seen_objects:
      return True
    
    seen_objects = seen_objects + [other_id]
    
    for field_name in self.__dict__:
      self_val = self.__dict__[field_name]
      self_type = type(self_val)
      other_val = other.__dict__[field_name]
      other_type = type(other_val)
      if self_type != other_type:
        return False
      
      if isinstance(self_val, (list, tuple)):
        if len(self_val) != len(other_val):
          return False
        
        for i in range(len(self_val)):
          self_i = self_val[i]
          other_i = other_val[i]
          if isinstance(self_i, DBModel):
            if not self_i._recursive_equals(other, seen_objects):
              return False
          elif self_i != other_i:
            return False
        
        continue
      
      if isinstance(self_val, DBModel):
        if not self_val._recursive_equals(other_val, seen_objects):
          return False
      elif self_val != other_val:
        return False
    
    return True
  
  def __hash__(self) -> int:
    return self._recursive_hash()
  
  def _recursive_hash(self, seen_objects:list = None) -> int:
    if seen_objects is None:
      seen_objects = []
    
    if self in seen_objects:
      return 0
    
    seen_objects = seen_objects + [self]
    
    result = 0
    
    field_names = [key for key in self.__dict__]
    field_names.sort()  # for consistency
    for field_name in field_names:
      field_hash = 0
      field_val = self.__dict__[field_name]
      if isinstance(field_val, (list, set, tuple)):
        for val_i in field_val:
          _next_hash = getattr(val_i, '_recursive_hash', None)
          if callable(_next_hash):
            field_hash = (field_hash * 397) ^ _next_hash(seen_objects)
          else:
            field_hash = (field_hash * 397) ^ hash(val_i)
      else:
        _next_hash = getattr(field_val, '_recursive_hash', None)
        if callable(_next_hash):
          field_hash = _next_hash(seen_objects)
        else:
          field_hash = hash(field_val)
      
      result = (result * 397) ^ field_hash
    
    return result
  
  def _get_unique_id(self) -> str:
    raise NotImplementedException('abstract')

class Catalog(DBModel):
  def __init__(self, id:int, name:str, lcase_name:str, no_diacritic_name:str, lcase_no_diacritic_name:str, base_path:str):
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
    
    if base_path is not None and not isinstance(base_path, str):
      grievances.append('a base path must be a str.')
    
    if len(grievances) > 0:
      raise InvalidCatalogDataException('\n'.join(grievances))
    
    self._id = id
    self._name = name
    self._lcase_name = lcase_name
    self._no_diacritic_name = no_diacritic_name
    self._lcase_no_diacritic_name = lcase_no_diacritic_name
    self._base_path = base_path
    
    if lcase_name is None or no_diacritic_name is None or lcase_no_diacritic_name is None:
      self.set_name(name)
  
  def __eq__(self, other) -> bool:
    return isinstance(other, Catalog) and \
      self._id == other._id and \
      self._name == other._name and \
      self._base_path == other._base_path
  
  def __ne__(self, other) -> bool:
    return not self.__eq__(other)
  
  def __hash__(self) -> int:
    return (((hash(self._id)*397) ^ hash(self._name))*397) ^ hash(self._base_path)
  
  def __str__(self) -> str:
    return self.get_name() + ' (' + self.get_base_path() + ')'
  
  def _get_unique_id(self) -> str:
    return '%s#%s' % (get_type_name(self), self.get_id())
  
  def get_id(self) -> int:
    return self._id
  
  def get_name(self) -> str:
    return self._name
  
  def set_name(self, name:str) -> None:
    if not isinstance(name, str):
      raise ValueError('a name must be a str.')
    
    self._name = name
    self._lcase_name, self._no_diacritic_name, self._lcase_no_diacritic_name = get_search_text_from_raw_text(name)
  
  def get_lcase_name(self) -> str:
    return self._lcase_name
  
  def get_no_diacritic_name(self) -> str:
    return self._no_diacritic_name
  
  def get_lcase_no_diacritic_name(self) -> str:
    return self._lcase_no_diacritic_name
  
  def get_base_path(self) -> str:
    return self._base_path
  
  def set_base_path(self, base_path:str) -> None:
    if not isinstance(base_path, str):
      raise ValueError('a base path must be a str.')
    
    self._base_path = base_path
  
  def get_base_flac_dir(self) -> str:
    return self._get_base_dir('flac')
  
  def get_base_mp3_dir(self) -> str:
    return self._get_base_dir('mp3')
  
  def get_base_broken_metadata_dir(self) -> str:
    return self._get_base_dir('fix metadata')
  
  def _get_base_dir(self, file_type:str) -> str:
    return '%s/%s' % (self.get_base_path(), file_type)
  
  def get_full_song_filename_validation_error(self, full_filename:str) -> str:
    if not isinstance(full_filename, str):
      return 'a filename must be a string.'
    
    if '.' not in full_filename:
      return 'a song\'s filename must have an extension.'
    
    extension = full_filename[full_filename.rfind('.') + 1:]
    if full_filename[:len(self._base_path) + 1 + len(extension) + 1] != '%s/%s/' % (self._base_path, extension):
      return 'a song\'s full filename must start with its catalog\'s base path and then have a folder with the file\'s extension.'
    
    return None
  
  def get_song_filename_from_full_filename(self, full_filename:str) -> str:
    if not isinstance(full_filename, str):
      raise TypeError('a filename must be a string.')
    
    if '.' not in full_filename:
      raise ValueError('a song\'s filename must have an extension.')
    
    extension = full_filename[full_filename.rfind('.') + 1:]
    beginning_len = len(self._base_path) + 1 + len(extension)
    beginning = full_filename[:beginning_len]
    expected = '%s%s/' % (self._base_path, extension)
    if beginning != expected:
      raise ValueError('a song\'s full filename must start with its catalog\'s base path and then have a folder with the file\'s extension.')
    
    return full_filename[beginning_len:]

def song_album_key(s_al):
  return s_al.get_track_number()

def song_artist_key(s_ar):
  return s_ar.get_list_order()

class Song(DBModel):
  def __init__(self, id:int,
               title:str, lcase_title:str, no_diacritic_title:str, lcase_no_diacritic_title:str,
               year:int, duration:float, title_minimum_age:int, lyrics_minimum_age:int,
               mp3_file_size:int, flac_file_size:int, filename:str, file_last_modified:int,
               catalog:Catalog, genres = None, songs_albums = None, songs_artists = None,
               song_similarities_from_song1 = None, song_similarities_from_song2 = None,
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
    
    if title_minimum_age is not None and not isinstance(title_minimum_age, int):
      grievances.append('a song title\'s minimum age must be an int.')
    
    if lyrics_minimum_age is not None and not isinstance(lyrics_minimum_age, int):
      grievances.append('a song lyrics\' minimum age must be an int.')
    
    if not isinstance(mp3_file_size, int):
      grievances.append('an mp3 file size must be an int.')
    
    if flac_file_size is not None and not isinstance(flac_file_size, int):
      grievances.append('a flac file size must be an int.')
    
    if not isinstance(filename, str):
      grievances.append('a filename must be a str.')
    elif filename.endswith('.mp3'):
      filename = filename[:-4]
    elif filename.endswith('.flac'):
      filename = filename[:-5]
    
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
    self._title_minimum_age = title_minimum_age
    self._lyrics_minimum_age = lyrics_minimum_age
    self._mp3_file_size = mp3_file_size
    self._flac_file_size = flac_file_size
    self._filename = filename
    self._catalog = catalog
    self._last_scanned = last_scanned
    self._file_last_modified = file_last_modified
    self._genres = list(genres)
    self._songs_albums = songs_albums
    self._songs_artists = songs_artists
    self._song_similarities_from_song2 = list(song_similarities_from_song2)
    self._song_similarities_from_song1 = list(song_similarities_from_song1)
  
  def __str__(self) -> str:
    return '"' + self.get_title() + '" by ' + ''.join([s_a.get_artist().get_name() + ('' if s_a.get_conjunction() is None else s_a.get_conjunction()) for s_a in self.get_songs_artists()])
  
  def _get_unique_id(self) -> str:
    return '%s#%s' % (get_type_name(self), self.get_id())
  
  def get_id(self) -> int:
    return self._id
  
  def set_id(self, id:int):
    if not isinstance(id, int):
      raise ValueError('an id must be an int.')
    
    self._id = id
  
  def get_title(self) -> str:
    return self._title
  
  def set_title(self, title:str) -> None:
    if not isinstance(title, str):
      raise ValueError('a song title must be a str.')
    
    self._title = title
    self._lcase_title, self._no_diacritic_title, self._lcase_no_diacritic_title = get_search_text_from_raw_text(title)
  
  def get_lcase_title(self) -> str:
    return self._lcase_title
  
  def get_no_diacritic_title(self) -> str:
    return self._no_diacritic_title
  
  def get_lcase_no_diacritic_title(self) -> str:
    return self._lcase_no_diacritic_title
  
  def get_year(self) -> int:
    return self._year
  
  def set_year(self, year:int) -> None:
    if not isinstance(year, int):
      raise ValueError('a year must be an int.')
    
    self._year = year
  
  def get_duration(self) -> float:
    return self._duration
  
  def set_duration(self, duration:float) -> None:
    if not isinstance(duration, float):
      raise ValueError('a duration must be a float.')
    
    self._duration = duration
  
  def get_title_minimum_age(self) -> int:
    return self._title_minimum_age
  
  def set_title_minimum_age(self, title_minimum_age:int) -> None:
    if title_minimum_age is not None and not isinstance(title_minimum_age, int):
      raise TypeError('a title\'s minimum age must be an int.')
    
    if title_minimum_age < 0:
      raise ValueError('a title\'s minimum age must be nonnegative.')
    
    self._title_minimum_age = title_minimum_age
  
  def get_lyrics_minimum_age(self) -> int:
    return self._lyrics_minimum_age
  
  def set_lyrics_minimum_age(self, lyrics_minimum_age:int) -> None:
    if lyrics_minimum_age is not None and not isinstance(lyrics_minimum_age, int):
      raise TypeError('lyrics\' minimum age must be an int.')
    
    if lyrics_minimum_age < 0:
      raise ValueError('lyrics\' minimum age must be nonnegative.')
    
    self._lyrics_minimum_age = lyrics_minimum_age
  
  def get_filename(self) -> str:
    return self._filename
  
  def get_mp3_filename(self) -> str:
    return self._get_file_type_filename(AudioFileTypes.MP3)
  
  def get_flac_filename(self) -> str:
    return self._get_file_type_filename(AudioFileTypes.FLAC)
  
  def _get_file_type_filename(self, file_type:AudioFileTypes) -> str:
    return '%s.%s' % (self.get_filename(), file_type.value)
  
  def set_filename(self, filename:str) -> None:
    if not isinstance(filename, str):
      raise TypeError('a filename must be a str.')
    
    full_filename = self.get_catalog().get_base_path() + filename + '.' + AudioFileTypes.MP3.value
    if not os.path.exists(full_filename):
      raise ValueError('the file "%s" doesn\'t exist.' % (full_filename, ))
    
    self._filename = filename
    self._mp3_file_size = get_file_size_in_bytes(full_filename)
    
    full_filename = self.get_catalog().get_base_path() + filename + '.' + AudioFileTypes.FLAC.value
    self._flac_file_size = get_file_size_in_bytes(full_filename) if os.path.exists(full_filename) else None
  
  def get_full_filename(self) -> str:
    return self.get_catalog().get_base_path() + self.get_filename()
  
  def get_mp3_file_size_in_bytes(self) -> int:
    return self._mp3_file_size
  
  def get_flac_file_size_in_bytes(self) -> int:
    return self._flac_file_size
  
  def get_last_scanned(self) -> int:
    return self._last_scanned
  
  def set_last_scanned(self, last_scanned:int) -> None:
    if not isinstance(last_scanned, int):
      raise ValueError('a last scanned timestamp must be an int.')
    
    self._last_scanned = last_scanned
  
  def get_file_last_modified(self) -> int:
    return self._file_last_modified
  
  def set_file_last_modified(self, file_last_modified:int) -> None:
    if not isinstance(file_last_modified, int):
      raise ValueError('a last modified timestamp must be an int.')
  
    self._file_last_modified = file_last_modified
  
  def get_catalog(self) -> Catalog:
    return self._catalog
  
  def set_catalog(self, catalog) -> None:
    self._catalog = catalog
  
  def get_genres(self) -> list:
    return self._genres
  
  def set_genres(self, genres) -> None:
    if not is_iterable(genres):
      raise TypeError('a collection of genres must be iterable.')
    
    self._genres = set(genres)
  
  def get_songs_albums(self) -> list:
    return self._songs_albums
  
  def set_songs_albums(self, songs_albums) -> None:
    if not is_iterable(songs_albums):
      raise TypeError('songs_albums must be iterable.')
    
    songs_albums = list(songs_albums)
    songs_albums.sort(key=song_album_key)
    
    self._songs_albums = songs_albums
  
  def get_songs_artists(self) -> list:
    return self._songs_artists
  
  def set_songs_artists(self, songs_artists) -> None:
    if not is_iterable(songs_artists):
      raise TypeError('songs_artists must be iterable.')
    
    songs_artists = list(songs_artists)
    songs_artists.sort(key=song_artist_key)
    
    self._songs_artists = songs_artists
  
  def get_song_similarities_from_song2(self) -> list:
    return self._song_similarities_from_song2
  
  def set_song_similarities_from_song2(self, song_similarities_from_song2) -> None:
    self._song_similarities_from_song2 = song_similarities_from_song2
  
  def get_song_similarities_from_song1(self) -> list:
    return self._song_similarities_from_song1
  
  def set_song_similarities_from_song1(self, song_similarities_from_song1) -> None:
    self._song_similarities_from_song1 = song_similarities_from_song1

class Artist(DBModel):
  def __init__(self, id:int, name:str, lcase_name:str, no_diacritic_name:str, lcase_no_diacritic_name:str, songs_artists = None, albums = None):
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
    
    if len(grievances) > 0:
      raise InvalidArtistDataException('\n'.join(grievances))
    
    self._id = id
    self._name = name
    self._lcase_name = lcase_name
    self._no_diacritic_name = no_diacritic_name
    self._lcase_no_diacritic_name = lcase_no_diacritic_name
    self._songs_artists = songs_artists
    self._albums = albums
    self._genres = None
    
    if lcase_name is None or no_diacritic_name is None or lcase_no_diacritic_name is None:
      self.set_name(name)
  
  def __str__(self) -> str:
    return self._name
  
  def _get_unique_id(self) -> str:
    return '%s#%s' % (get_type_name(self), self.get_id())
  
  def get_id(self) -> int:
    return self._id
  
  def get_name(self) -> str:
    return self._name
  
  def set_name(self, name:str) -> None:
    if not isinstance(name, str):
      raise ValueError('a name must be a str.')
    
    self._name = name
    self._lcase_name, self._no_diacritic_name, self._lcase_no_diacritic_name = get_search_text_from_raw_text(name)
  
  def get_lcase_name(self) -> str:
    return self._lcase_name
  
  def get_no_diacritic_name(self) -> str:
    return self._no_diacritic_name
  
  def get_lcase_no_diacritic_name(self) -> str:
    return self._lcase_no_diacritic_name
  
  def get_songs_artists(self) -> list:
    return self._songs_artists
  
  def set_songs_artists(self, songs_artists) -> None:
    self._songs_artists = songs_artists
  
  def get_albums(self) -> list:
    return self._albums
  
  def set_albums(self, albums) -> None:
    self._albums = albums
  
  def get_genres(self) -> list:
    return self._genres
  
  def set_genres(self, genres:list) -> None:
    if not isinstance(genres, list):
      raise TypeError('an artist\'s genres must be a list of genres.')
    
    self._genres = genres

class SongArtist(DBModel):
  def __init__(self, song:Song, artist:Artist, list_order:int, conjunction:str = ''):
    grievances = []
    
    if list_order is not None and not isinstance(list_order, int):
      grievances.append('a list order must be an int.')
    
    if conjunction is not None and not isinstance(conjunction, str):
      grievances.append('a conjunction must be a str.')
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    self._list_order = list_order
    self._song = song
    self._artist = artist
    self._conjunction = conjunction
  
  def _get_unique_id(self) -> str:
    return '%s#%s|%s' % (get_type_name(self), self.get_song().get_id(), self.get_artist().get_id())
  
  def get_song(self) -> Song:
    return self._song
  
  def set_song(self, song:Song) -> None:
    self._song = song
  
  def get_artist(self) -> Artist:
    return self._artist
  
  def set_artist(self, artist:Artist):
    self._artist = artist
  
  def get_list_order(self) -> int:
    return self._list_order
  
  def set_list_order(self, list_order:int) -> None:
    if not isinstance(list_order, int):
      raise ValueError('a list order must be an int.')
  
    self._list_order = list_order
  
  def get_conjunction(self) -> str:
    return self._conjunction
  
  def set_conjunction(self, conjunction:str) -> None:
    if not isinstance(conjunction, str):
      raise ValueError('a conjunction must be a str.')
    
    self._conjunction = conjunction

class Album(DBModel):
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
  
  def __str__(self) -> str:
    return self._name + ' by ' + self._album_artist.get_name() + ':\n' + \
      '\n'.join('  ' + str(s_a.get_track_number()) + '. ' + str(s_a.get_song()) for s_a in self._songs_albums)
  
  def _get_unique_id(self) -> str:
    return '%s#%s' % (get_type_name(self), self.get_id())
  
  def get_id(self) -> int:
    return self._id
  
  def get_name(self) -> str:
    return self._name
  
  def set_name(self, name:str) -> None:
    if not isinstance(name, str):
      raise ValueError('a name must be a str.')
    
    self._name = name
    
    self._lcase_name, self._no_diacritic_name, self._lcase_no_diacritic_name = get_search_text_from_raw_text(name)
  
  def get_lcase_name(self) -> str:
    return self._lcase_name
  
  def get_no_diacritic_name(self) -> str:
    return self._no_diacritic_name
  
  def get_lcase_no_diacritic_name(self) -> str:
    return self._name
  
  def get_album_artist(self) -> Artist:
    return self._album_artist
  
  def set_album_artist(self, album_artist:Artist) -> None:
    if not isinstance(album_artist, Artist):
      raise TypeError('an album artist must be an Artist.')
    
    self._album_artist = album_artist
  
  def get_songs_albums(self):
    return self._songs_albums
  
  def set_songs_albums(self, songs_albums) -> None:
    self._songs_albums = songs_albums

class SongAlbum(DBModel):
  def __init__(self, song:Song, album:Album, track_number:int):
    grievances = []
    
    if not isinstance(song, Song):
      grievances.append('a song must be a Song.')
    
    if not isinstance(album, Album):
      grievances.append('an album must be an Album.')
    
    if track_number is not None and not isinstance(track_number, int):
      grievances.append('a track number must be an int.')
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    self._song = song
    self._album = album
    self._track_number = track_number
  
  def _get_unique_id(self) -> str:
    return '%s#%s|%s' % (get_type_name(self), self.get_song().get_id(), self.get_album().get_id())
  
  def get_song(self) -> Song:
    return self._song
  
  def set_song(self, song:Song) -> None:
    if not isinstance(song, Song):
      raise TypeError('a song must be a Song.')
    
    self._song = song
  
  def get_album(self) -> Album:
    return self._album
  
  def set_album(self, album:Album) -> None:
    if not isinstance(album, Album):
      raise TypeError('an album must be an Album.')
    
    self._album = album
  
  def get_track_number(self) -> int:
    return self._track_number
  
  def set_track_number(self, track_number:int) -> None:
    if not isinstance(track_number, int):
      raise ValueError('a track number must be an int.')
    
    self._track_number = track_number

class Genre(DBModel):
  def __init__(self, id:int, name:str, lcase_name:str, no_diacritic_name:str, lcase_no_diacritic_name:str):
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
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    self._id = id
    self._name = name
    self._lcase_name = lcase_name
    self._no_diacritic_name = no_diacritic_name
    self._lcase_no_diacritic_name = lcase_no_diacritic_name
    
    if lcase_name is None or no_diacritic_name is None or lcase_no_diacritic_name is None:
      self.set_name(name)
  
  def __str__(self) -> str:
    return self._name
  
  def _get_unique_id(self) -> str:
    return '%s#%s' % (get_type_name(self), self.get_id())
  
  def get_id(self) -> int:
    return self._id
  
  def get_name(self) -> str:
    return self._name
  
  def set_name(self, name:str) -> None:
    if not isinstance(name, str):
      raise ValueError('a(n) name must be a(n) str.')
    
    self._name = name
    self._lcase_name, self._no_diacritic_name, self._lcase_no_diacritic_name = get_search_text_from_raw_text(name)
  
  def get_lcase_name(self) -> str:
    return self._lcase_name
  
  def get_no_diacritic_name(self) -> str:
    return self._no_diacritic_name
  
  def get_lcase_no_diacritic_name(self) -> str:
    return self._lcase_no_diacritic_name

class SongGenre(DBModel):
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
  
  def _get_unique_id(self) -> str:
    return '%s#%s|%s' % (get_type_name(self), self.get_song().get_id(), self.get_genre().get_id())
  
  def get_song(self) -> Song:
    return self._song
  
  def set_song(self, song) -> None:
    if not isinstance(song, Song):
      raise TypeError('a song must be a Song.')
    
    self._song = song
  
  def get_genre(self) -> Genre:
    return self._genre
  
  def set_genre(self, genre) -> None:
    if not isinstance(genre, Genre):
      raise TypeError('a genre must be a Genre.')
    
    self._genre = genre