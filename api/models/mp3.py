import re

from enum import Enum

from exceptions import InvalidMP3DataException
from util.logger import get_logger

class MP3Fields(Enum):
  FILENAME = 'filename'
  DATE_MODIFIED = 'date_modified'
  TITLE = 'title'
  ARTIST = 'artist'
  ALBUM_ARTIST = 'album_artist'
  ALBUM = 'album'
  TRACK = 'track'
  GENRE = 'genre'
  YEAR = 'date'
  COMMENT = 'comment'

def get_field(key, data, type_func):
  if key in data:
    get_logger().debug('for %s, found "%s"' % (str(key), str(data[key])))
    return type_func(data[key])
  
  get_logger().debug('didn\'t find any value for %s.' % str(key))
  return None

def get_track(data):
  if MP3Fields.TRACK.value not in data:
    get_logger().debug('found no track.')
    return None
  
  track = str(data[MP3Fields.TRACK.value])
  message = 'found the track data "%s"; ' % track
  
  num_with_ttl = re.compile('^\\d+\\/\\d+$')
  just_num = re.compile('^\\d+(\\.\\d+)?$')
  if isinstance(num_with_ttl.search(track), re.Match):
    track = int(track[0:track.index('/')])
  elif isinstance(num_with_ttl.search(track), re.Match):
    track = int(track)
  else:
    track = None
  
  message += 'setting the track to %s.' % str(track)
  get_logger().debug(message)
  return track

def get_year(data):
  if MP3Fields.YEAR.value not in data:
    return None
  
  raw_value = data[MP3Fields.YEAR.value]
  
  if raw_value is None or isinstance(raw_value, int):
    return raw_value
  
  if not isinstance(raw_value, str):
    get_logger().warn('found an invalid year "%s" of type %s; not saving it.' % (str(raw_value), str(type(raw_value))))
    return None
  
  pattern = re.compile('^\\d+(\\.\\d+)?$')
  if isinstance(pattern.search(raw_value), re.Match):
    return int(raw_value)

  pattern = re.compile('^\\d{4}\\-\\d{2}\\-\\d{2}$')
  if isinstance(pattern.search(raw_value), re.Match):
    return int(raw_value[0:4])
  
  get_logger().warn('found an unparsed date format: %s' % (raw_value, ))
  return None

class MP3:
  def __init__(self, data):
    if MP3Fields.FILENAME.value not in data.keys():
      raise InvalidMP3DataException('no filename was found.')
    
    if not isinstance(data[MP3Fields.FILENAME.value], str):
      raise InvalidMP3DataException('an mp3\'s filename must be a string.')
    
    if MP3Fields.DATE_MODIFIED.value not in data.keys():
      raise InvalidMP3DataException('no date modified was found.')
    
    if not isinstance(data[MP3Fields.DATE_MODIFIED.value], int):
      raise InvalidMP3DataException('the date modified must be the number of seconds since the unix epoc.')
    
    logger = get_logger()
    logger.debug('found mp3 metadata: %s' % str(data))
    
    self.filename = data[MP3Fields.FILENAME.value]
    self.date_modified = data[MP3Fields.DATE_MODIFIED.value]
    logger.debug('getting fields for %s (modified at %s)...' % (str(self.filename), str(self.date_modified)))
    
    self.title = get_field(MP3Fields.TITLE.value, data, str)
    self.artist = get_field(MP3Fields.ARTIST.value, data, str)
    self.album_artist = get_field(MP3Fields.ALBUM_ARTIST.value, data, str)
    self.album = get_field(MP3Fields.ALBUM.value, data, str)
    self.track = get_track(data)
    self.genre = get_field(MP3Fields.GENRE.value, data, str)
    self.year = get_year(data)
    self.comment = get_field(MP3Fields.COMMENT.value, data, str)
  
  def __str__(self):
    return '%s by %s' % (self.title, self.artist)