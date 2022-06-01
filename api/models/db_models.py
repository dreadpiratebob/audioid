from models.catalog import Catalog
from exceptions import InvalidAlbumDataException
from exceptions import InvalidArtistDataException
from exceptions import InvalidGenreDataException
from exceptions import InvalidSongDataException

class Song:
  def __init__(self, id, title, year, filename, last_scanned, file_last_modified, catalog):
    if id is not None and not isinstance(id, int):
      raise InvalidSongDataException('a song id must be an int.  (found "%s" of type %s instead.)' % (str(id), str(type(id))))
    
    if title is not None and not isinstance(title, str):
      raise InvalidSongDataException('a song title must be a str.  (found "%s" of type %s instead.)' % (str(title), str(type(title))))
    
    if year is not None and not isinstance(year, int):
      raise InvalidSongDataException('a song year must be an int.  (found "%s" of type %s instead.)' % (str(year), str(type(year))))
    
    if not isinstance(filename, str):
      raise InvalidSongDataException('a filename must be a str.  (found "%s" of type %s instead.)' % (str(filename), str(type(filename))))
    
    if last_scanned is not None and not isinstance(last_scanned, int):
      raise InvalidSongDataException('the last_scanned timestamp must be an int.  (found "%s" of type %s instead.)' % (str(last_scanned), str(type(last_scanned))))
    
    if not isinstance(file_last_modified, int):
      raise InvalidSongDataException('the file_last_modified timestamp must be an int.  (found "%s" of type %s instead.)' % (str(file_last_modified), str(type(file_last_modified))))
    
    if not isinstance(catalog, Catalog):
      raise InvalidSongDataException('a catalog must be of type Catalog.  (found "%s" of type %s instead.)' % (str(catalog), str(type(catalog))))
    
    self.id = id
    self.title = title
    self.year = year
    self.filename = filename
    self.last_scanned = last_scanned
    self.file_last_modified = file_last_modified
    self.catalog = catalog
    
    self.artists = None
    self.albums = None
    self.genres = None
  
  def __str__(self):
    if self.artists is None:
      raise InvalidSongDataException('someone tried to convert a song with no artist data to a string.')
    
    if self.albums is None:
      raise InvalidSongDataException('someone tried to convert a song with no album data to a string.')
    
    artists = ''
    for artist_join in self.artists:
      artists += artist_join.artist.name + ('' if artist_join.conjunction is None else artist_join.conjunction)
    
    albums = ''
    for album_join in self.albums:
      albums += '%s on %s and ' % (str(album_join.track), album_join.album.name)
    albums = albums[0:len(albums) - 5]
    
    return '%s by %s, track %s from the year %s' % (self.title, artists, albums, 'UNK' if self.year is None else str(self.year))

class Artist:
  def __init__(self, id, name):
    if id is not None and not isinstance(id, int):
      raise InvalidArtistDataException('an artist id must be an int.  (found "%s" of type %s instead.)' % (str(id), str(type(id))))
    
    if not isinstance(name, str):
      raise InvalidArtistDataException('an artist name must be a str.  (found "%s" of type %s instead.)' % (str(name), str(type(name))))
    
    self.id = id
    self.name = name
  
  def __str__(self):
    return self.name

class ArtistJoin:
  def __init__(self, song, artist, list_order, conjunction = None):
    if not isinstance(song, Song):
      raise InvalidSongDataException('a song must be of type Song. (found "%s" of type %s instead.)' % (str(song), str(type(song))))
    
    if not isinstance(artist, Artist):
      raise InvalidArtistDataException('an artist must be of type Artist. (found "%s" of type %s instead.)' % (str(artist), str(type(artist))))
    
    if not isinstance(list_order, int):
      raise InvalidArtistDataException('a list order must be of type int. (found "%s" of type %s instead.)' % (str(list_order), str(type(list_order))))
    
    if conjunction is not None and not isinstance(conjunction, str):
      raise InvalidArtistDataException('a conjunction must be of type string. (found "%s" of type %s instead.)' % (str(conjunction), str(type(conjunction))))
    
    self.song = song
    self.artist = artist
    self.list_order = list_order
    self.conjunction = conjunction
  
  def __str__(self):
    return 'joining the song "%s" to the artist %s with %s' % (self.song.title, self.artist.name, 'None' if self.conjunction is None else '"%s"' % self.conjunction)

class Album:
  def __init__(self, id, name, album_artist):
    if id is not None and not isinstance(id, int):
      raise InvalidAlbumDataException('a list order must be of type int. (found "%s" of type %s instead.)' % (str(id), str(type(id))))
    
    if not isinstance(name, str):
      raise InvalidAlbumDataException('an album name must be of type str. (found "%s" of type %s instead.)' % (str(name), str(type(name))))
    
    if not isinstance(album_artist, Artist):
      raise InvalidAlbumDataException('an album artist must be of type Artist. (found "%s" of type %s instead.)' % (str(album_artist), str(type(album_artist))))
    
    self.id = id
    self.name = name
    self.album_artist = album_artist
  
  def __str__(self):
    return '%s by %s' % (self.name, str(self.album_artist))

class SongAlbum:
  def __init__(self, song, album, track):
    if not isinstance(song, Song):
      raise InvalidSongDataException('a song must be of type Song. (found "%s" of type %s instead.)' % (str(song), str(type(song))))
  
    if not isinstance(album, Album):
      raise InvalidAlbumDataException('an artist must be of type Artist. (found "%s" of type %s instead.)' % (str(album), str(type(album))))
  
    if track is not None and not isinstance(track, int):
      raise InvalidAlbumDataException('a track number must be of type int. (found "%s" of type %s instead.)' % (str(track), str(type(track))))
    
    self.song = song
    self.album = album
    self.track = track
  
  def __str__(self):
    return 'joining the song "%s" to the album "%s" as track number %s' % (self.song.title, self.album.name, str(self.track))

class Genre:
  def __init__(self, id, name):
    if id is not None and not isinstance(id, int):
      raise InvalidGenreDataException('a genre id must be an int.  (found "%s" of type %s instead.)' % (str(id), str(type(id))))
    
    if not isinstance(name, str):
      raise InvalidGenreDataException('a genre name must be a str.  (found "%s" of type %s instead.)' % (str(name), str(type(name))))
    
    self.id = id
    self.name = name
  
  def __str__(self):
    return self.name

class SongGenre:
  def __init__(self, song, genre):
    if not isinstance(song, Song):
      raise InvalidSongDataException('a song must be of type Song. (found "%s" of type %s instead.)' % (str(song), str(type(song))))
  
    if not isinstance(genre, Genre):
      raise InvalidGenreDataException('an artist must be of type Artist. (found "%s" of type %s instead.)' % (str(album), str(type(album))))
    
    self.song = song
    self.genre = genre
  
  def __str__(self):
    return 'joining the song "%s" to the genre "%s"' % (self.song.title, self.genre.name)