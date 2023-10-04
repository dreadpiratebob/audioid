from api.exceptions.song_data import InvalidMP3DataException
from api.util.logger import get_logger

import re

from enum import Enum

class MP3Fields(Enum):
  FILENAME = 'filename'
  DATE_MODIFIED = 'date_modified'
  DURATION = 'duration'
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
  elif isinstance(just_num.search(track), re.Match):
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
  
  get_logger().debug('for year, found the raw value "%s"...' % str(raw_value))
  
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
    grievances = []
  
    if MP3Fields.FILENAME.value not in data:
      grievances.append('no filename was found.')
    elif not isinstance(data[MP3Fields.FILENAME.value], str):
      grievances.append('an mp3\'s filename must be a string.')
  
    if MP3Fields.DATE_MODIFIED.value not in data:
      grievances.append('no date modified was found.')
    elif not isinstance(data[MP3Fields.DATE_MODIFIED.value], int):
      grievances.append('the date modified must be the number of seconds since the unix epoc.')
  
    if MP3Fields.DURATION.value not in data:
      grievances.append('no duration was found.')
    elif not isinstance(data[MP3Fields.DURATION.value], float):
      grievances.append('a duration must be a float.')
  
    if len(grievances) > 0:
      raise InvalidMP3DataException('\n'.join(grievances))
  
    logger = get_logger()
    
    self.filename = data[MP3Fields.FILENAME.value]
    self.date_modified = data[MP3Fields.DATE_MODIFIED.value]
    
    self.title = get_field(MP3Fields.TITLE.value, data, str)
    self.duration = data[MP3Fields.DURATION.value]
    self.artist = get_field(MP3Fields.ARTIST.value, data, str)
    self.album_artist = get_field(MP3Fields.ALBUM_ARTIST.value, data, str)
    self.album = get_field(MP3Fields.ALBUM.value, data, str)
    self.track = get_track(data)
    self.genre = get_field(MP3Fields.GENRE.value, data, str)
    self.year = get_year(data)
    self.comment = get_field(MP3Fields.COMMENT.value, data, str)
    
    logger.debug('for duration, found ' + str(self.duration))
  
  def __str__(self):
    return '%s by %s' % (self.title, self.artist)