from api.exceptions.song_data import InvalidMP3DataException
from api.util.functions import get_type_name
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
  DATE = 'date', {'date', 'DATE'}
  DATE_MODIFIED = 'date_modified', {'date_modified'}
  DURATION = 'duration', {'duration'}
  ENCODER = 'encoder', {'encoder'}
  FLAC_FILE_SIZE = 'flac_file_size', {'flac_file_size'}
  MP3_FILE_SIZE = 'mp3_file_size', {'mp3_file_size'}
  TITLE = 'title', {'title', 'TITLE', 'TIT2'}
  ARTIST = 'artist', {'artist', 'ARTIST', 'TPE1'}
  ALBUM_ARTIST = 'album_artist', {'album_artist'}
  ALBUM = 'album', {'album', 'ALBUM', 'TALB'}
  TRACK = 'track', {'track', 'TRACK', 'TRCK'}
  GENRE = 'genre', {'genre', 'GENRE', 'TCON'}
  YEAR = 'year', {'year', 'DATE', 'TDRC'}
  COMMENT = 'comment', {'comment', 'COMMENT'}

_audio_metadata_fields_by_key = {f.field_name: f for f in AudioMetadataFields}
for f in AudioMetadataFields:
  for key in f.other_names:
    _audio_metadata_fields_by_key[key] = f
def get_audio_metadata_field(name:str) -> AudioMetadataFields:
  if not isinstance(name, str) or name not in _audio_metadata_fields_by_key:
    raise ValueError('unknown metadata field "%s".' % (name, ))
  
  return _audio_metadata_fields_by_key[name]

def _get_field(field:AudioMetadataFields, data:dict[AudioMetadataFields, str], type_func, verbose:bool = False) -> any:
  if field in data:
    if verbose:
      get_logger().debug('for %s, found "%s"' % (field.field_name, str(data[field])))
    return type_func(data[field])
  
  if verbose:
    get_logger().debug('didn\'t find any value for %s.' % str(field.field_name))
  return None

_num_with_ttl = re.compile('^\\d+/\\d+$')
_just_num = re.compile('^\\d+(\\.\\d+)?$')
def _get_track(data:dict[AudioMetadataFields, str], verbose:bool = False) -> int:
  track = _get_field(AudioMetadataFields.TRACK, data, str, verbose)
  if track is None:
    return None
  
  message = ''
  if verbose:
    message = 'found the track data "%s"; ' % track
  
  if isinstance(_num_with_ttl.search(track), re.Match):
    track = int(track[0:track.index('/')])
  elif isinstance(_just_num.search(track), re.Match):
    track = int(track)
  else:
    track = None
  
  if verbose:
    message += 'setting the track to %s.' % str(track)
    get_logger().debug(message)
  
  return track

def _get_year(data:dict[AudioMetadataFields, str], verbose:bool = False) -> int:
  raw_value = _get_field(AudioMetadataFields.YEAR, data, str, verbose)
  
  if verbose:
    get_logger().debug('for year, found the raw value "%s"...' % str(raw_value))
  
  if raw_value is None or isinstance(raw_value, int):
    return raw_value
  
  if not isinstance(raw_value, str):
    get_logger().warn('found an invalid year "%s" of type %s; not saving it.' % (str(raw_value), get_type_name(raw_value)))
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
  def __init__(self, data:dict, verbose:bool = False):
    grievances = []
    
    if AudioMetadataFields.FILENAME not in data:
      grievances.append('no filename was found.')
    elif not isinstance(data[AudioMetadataFields.FILENAME], str):
      grievances.append('an mp3\'s filename must be a string.')
    
    if AudioMetadataFields.DATE_MODIFIED not in data:
      grievances.append('no date modified was found.')
    elif not isinstance(data[AudioMetadataFields.DATE_MODIFIED], int):
      grievances.append('the date modified must be the number of seconds since the unix epoc.')
    
    if AudioMetadataFields.DURATION not in data:
      data[AudioMetadataFields.DURATION] = None
    elif data[AudioMetadataFields.DURATION] is not None and not isinstance(data[AudioMetadataFields.DURATION], float):
      grievances.append('a duration must be a float.')
    
    if len(grievances) > 0:
      raise InvalidMP3DataException('\n'.join(grievances))
    
    self.filename = str(data[AudioMetadataFields.FILENAME]).replace('\\', '/')
    self.date_modified = data[AudioMetadataFields.DATE_MODIFIED]
    
    self.title = _get_field(AudioMetadataFields.TITLE, data, str, verbose)
    self.duration = data[AudioMetadataFields.DURATION]
    self.artist = _get_field(AudioMetadataFields.ARTIST, data, str, verbose)
    self.album_artist = _get_field(AudioMetadataFields.ALBUM_ARTIST, data, str, verbose)
    self.album = _get_field(AudioMetadataFields.ALBUM, data, str, verbose)
    self.track = _get_track(data, verbose)
    self.genre = _get_field(AudioMetadataFields.GENRE, data, str, verbose)
    self.year = _get_year(data, verbose)
    self.comment = _get_field(AudioMetadataFields.COMMENT, data, str, verbose)
    self.mp3_file_size = data[AudioMetadataFields.MP3_FILE_SIZE]
    self.mp3_exists = True
    self.flac_file_size = data[AudioMetadataFields.FLAC_FILE_SIZE]
    
    if self.title is None:
      self.title = self.filename[self.filename.rfind('/') + 1:self.filename.rfind('.')]
    
    if verbose:
      get_logger().debug('for duration, found ' + str(self.duration))
  
  def __str__(self) -> str:
    return '\n'.join('%s: %s' % (field, self.__dict__[field]) for field in self.__dict__)