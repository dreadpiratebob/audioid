from api.exceptions.song_data import InvalidMP3DataException
from api.models.audio_metadata_fields import AudioMetadataFields
from api.util.functions import get_type_name
from api.util.logger import get_logger

import re

class AudioMetadata:
  def __init__(self, data:dict, dedup_values:bool = False, verbose:bool = False):
    if data is None:
      self.filename = None
      self.date_modified = None
  
      self.title = None
      self.duration = None
      self.artist = None
      self.album_artist = None
      self.album = None
      self.track = None
      self.genre = None
      self.year = None
      self.comment = None
      self.mp3_file_size = None
      self.mp3_exists = None
      self.flac_file_size = None
      return
    
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
    
    self.title = _get_field(AudioMetadataFields.TITLE, data, str, dedup_values, verbose)
    self.duration = data[AudioMetadataFields.DURATION]
    self.artist = _get_field(AudioMetadataFields.ARTIST, data, str, dedup_values, verbose)
    self.album_artist = _get_field(AudioMetadataFields.ALBUM_ARTIST, data, str, dedup_values, verbose)
    self.album = _get_field(AudioMetadataFields.ALBUM, data, str, dedup_values, verbose)
    self.track = _get_track(data, dedup_values, verbose)
    self.genre = _get_field(AudioMetadataFields.GENRE, data, str, dedup_values, verbose)
    self.year = _get_year(data, dedup_values, verbose)
    self.comment = _get_field(AudioMetadataFields.COMMENT, data, str, dedup_values, verbose)
    self.mp3_file_size = data[AudioMetadataFields.MP3_FILE_SIZE]
    self.mp3_exists = True
    self.flac_file_size = data[AudioMetadataFields.FLAC_FILE_SIZE]
    
    if self.title is None:
      self.title = self.filename[self.filename.rfind('/') + 1:self.filename.rfind('.')]
    
    if verbose:
      get_logger().debug('for duration, found ' + str(self.duration))
  
  def __eq__(self, other):
    if not isinstance(other, type(self)):
      return False
    
    for field in self.__dict__:
      if self.__dict__[field] != other.__dict__[field]:
        return False
    
    return True
  
  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __hash__(self):
    result = 0
    
    fields = [f for f in self.__dict__]
    fields.sort()
    for field in fields:
      result = (result*397) ^ hash(self.__dict__[field])
    
    return result
  
  def __str__(self) -> str:
    return '\n'.join('%s: %s' % (field, self.__dict__[field]) for field in self.__dict__)

_dupable_fields = {'title', 'artist', 'album_artist', 'album', 'genre'}
def dedup_audio_metadata(audio_metadata:AudioMetadata) -> AudioMetadata:
  if not isinstance(audio_metadata, AudioMetadata):
    raise TypeError('audio metadata must be an AudioMetadata.')
  
  result = AudioMetadata(None)
  for field in audio_metadata.__dict__:
    val = audio_metadata.__dict__[field]
    if field in _dupable_fields:
      val = _dedup_value(val)
    
    result.__dict__[field] = val
  
  return result

def _dedup_value(val:str) -> str:
  tokens = val.split(';')
  
  for token in tokens[1:]:
    if token != tokens[0]:
      return val
  
  return tokens[0]

def _get_field(field:AudioMetadataFields, data:dict[AudioMetadataFields, str], type_func, dedup_value:bool = True, verbose:bool = False) -> any:
  if field in data:
    if verbose:
      get_logger().debug('for %s, found "%s"' % (field.field_name, str(data[field])))
    
    raw_value = data[field]
    if dedup_value:
      raw_value = _dedup_value(raw_value)
    
    return type_func(raw_value)
  
  if verbose:
    get_logger().debug('didn\'t find any value for %s.' % str(field.field_name))
  return None

_num_with_ttl = re.compile('^\\d+/\\d+$')
_just_num = re.compile('^\\d+(\\.\\d+)?$')
def _get_track(data:dict[AudioMetadataFields, str], dedup_value:bool = True, verbose:bool = False) -> int:
  track = _get_field(AudioMetadataFields.TRACK, data, str, dedup_value, verbose)
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

def _get_year(data:dict[AudioMetadataFields, str], dedup_value:bool = True, verbose:bool = False) -> int:
  raw_value = _get_field(AudioMetadataFields.YEAR, data, str, dedup_value, verbose)
  
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
  
  get_logger().warn('found an unparsed date format: %s' % (raw_value,))
  return None