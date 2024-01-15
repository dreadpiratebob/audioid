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
