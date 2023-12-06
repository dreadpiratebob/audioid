from api.exceptions.song_data import InvalidMP3DataException
from api.util.logger import get_logger

import re

from enum import Enum

class AudioMetadataFields(Enum):
  def __new__(self, *args, **kwds):
    value = len(self.__members__) + 1
    obj = object.__new__(self)
    obj._value_ = value
    return obj
  
  def __init__(self, field_name:str, other_names:set[str]):
    self.field_name  = field_name
    self.other_names = other_names
  
  FILENAME = 'filename', {'filename'}
  DATE_MODIFIED = 'date_modified', {'date_modified'}
  DURATION = 'duration', {'duration'}
  FILE_SIZE = 'file_size', {'file_size'}
  TITLE = 'title', {'title', 'TITLE', 'TIT2'}
  ARTIST = 'artist', {'artist', 'ARTIST', 'TPE1'}
  ALBUM_ARTIST = 'album_artist', {'album_artist'}
  ALBUM = 'album', {'album', 'ALBUM', 'TALB'}
  TRACK = 'track', {'track', 'TRACK', 'TRCK'}
  GENRE = 'genre', {'genre', '', 'TCON'}
  YEAR = 'year', {'year', 'DATE', 'TDRC'}
  COMMENT = 'comment', {'comment', 'COMMENT'}

_audio_metadata_fields_by_key = {f.field_name: f for f in AudioMetadataFields}
for f in AudioMetadataFields:
  for key in f.other_names:
    _audio_metadata_fields_by_key[key] = f
def get_audio_metadat_field(name:str) -> AudioMetadataFields:
  if not isinstance(name, str) or name not in _audio_metadata_fields_by_key:
    raise ValueError('unknown metadata field "%s".' % (name, ))
  
  return _audio_metadata_fields_by_key[name]

def _get_field(key:str, data:dict[str, str], type_func) -> any:
  if key in data:
    get_logger().debug('for %s, found "%s"' % (str(key), str(data[key])))
    return type_func(data[key])
  
  get_logger().debug('didn\'t find any value for %s.' % str(key))
  return None

def _get_track(data:dict[str, str]) -> int:
  if AudioMetadataFields.TRACK.value not in data:
    get_logger().debug('found no track.')
    return None
  
  track = str(data[AudioMetadataFields.TRACK.value])
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

def _get_year(data:dict[str, str]) -> int:
  if AudioMetadataFields.YEAR.value not in data:
    return None
  
  raw_value = data[AudioMetadataFields.YEAR.value]
  
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

class AudioMetadata:
  def __init__(self, data:dict):
    grievances = []
  
    if AudioMetadataFields.FILENAME.value not in data:
      grievances.append('no filename was found.')
    elif not isinstance(data[AudioMetadataFields.FILENAME.value], str):
      grievances.append('an mp3\'s filename must be a string.')
  
    if AudioMetadataFields.DATE_MODIFIED.value not in data:
      grievances.append('no date modified was found.')
    elif not isinstance(data[AudioMetadataFields.DATE_MODIFIED.value], int):
      grievances.append('the date modified must be the number of seconds since the unix epoc.')
  
    if AudioMetadataFields.DURATION.value not in data:
      grievances.append('no duration was found.')
    elif not isinstance(data[AudioMetadataFields.DURATION.value], float):
      grievances.append('a duration must be a float.')
  
    if len(grievances) > 0:
      raise InvalidMP3DataException('\n'.join(grievances))
  
    logger = get_logger()
    
    self.filename = data[AudioMetadataFields.FILENAME.value]
    self.date_modified = data[AudioMetadataFields.DATE_MODIFIED.value]
    
    self.title = _get_field(AudioMetadataFields.TITLE.value, data, str)
    self.duration = data[AudioMetadataFields.DURATION.value]
    self.artist = _get_field(AudioMetadataFields.ARTIST.value, data, str)
    self.album_artist = _get_field(AudioMetadataFields.ALBUM_ARTIST.value, data, str)
    self.album = _get_field(AudioMetadataFields.ALBUM.value, data, str)
    self.track = _get_track(data)
    self.genre = _get_field(AudioMetadataFields.GENRE.value, data, str)
    self.year = _get_year(data)
    self.comment = _get_field(AudioMetadataFields.COMMENT.value, data, str)
    
    logger.debug('for duration, found ' + str(self.duration))
  
  def __str__(self):
    return '%s by %s' % (self.title, self.artist)