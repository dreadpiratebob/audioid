from api.models.audio_metadata import \
  AudioMetadata
from api.models.audio_metadata_fields import AudioMetadataFields, _audio_metadata_fields_by_key, \
  get_audio_metadata_field
from api.util.file_operations import get_file_size_in_bytes, get_last_modified_timestamp
from api.util.logger import get_logger

import mutagen.mp3
import os
import re
import subprocess

_bad_filename_error_message = 'metadata can only be read from files with either a flac or an mp3 extension.'
_metadata_field_re = re.compile('^ +([a-zA-Z0-9_]+) +: (.*)$')
def read_metadata(filename:str, ffmpeg_output_from_conversion_to_mp3:str = None, verbose:bool = False, output_file_name:str = None) -> AudioMetadata:
  if not '.' in filename:
    raise ValueError(_bad_filename_error_message)
  
  extension = filename[filename.rfind('.') + 1:]
  if extension != 'mp3' and extension != 'flac':
    raise ValueError(_bad_filename_error_message)
  
  length         = None
  mp3_file_size  = None
  flac_file_size = None
  if extension == 'mp3':
    audio  = mutagen.mp3.MP3(filename)
    length = audio.info.length
    mp3_file_size = get_file_size_in_bytes(filename)
  elif extension == 'flac':
    flac_file_size = get_file_size_in_bytes(filename)
  
  data = \
  {
    AudioMetadataFields.DATE_MODIFIED: get_last_modified_timestamp(filename),
    AudioMetadataFields.FILENAME: filename,
    AudioMetadataFields.DURATION: length,
    AudioMetadataFields.FLAC_FILE_SIZE: flac_file_size,
    AudioMetadataFields.MP3_FILE_SIZE: mp3_file_size
  }
  
  if ffmpeg_output_from_conversion_to_mp3 is None:
    # ffmpeg -i filename -f ffmetadata outputfile
    outputfile = '%s metadata.txt' % filename
    subprocess.run(['ffmpeg', '-i', filename, '-f', 'ffmetadata', outputfile, '-y'], capture_output=True)
    
    if not os.path.exists(outputfile):
      get_logger().error('ffmpeg failed for "%s".' % (str(filename), ))
      return None
    
    lines = []
    with open(outputfile) as f:
      lines = f.readlines()
    
    if output_file_name is None:
      os.remove(outputfile)
    elif outputfile != output_file_name:
      subprocess.run(['mv', outputfile, output_file_name])
    
    for line in lines:
      if '=' not in line:
        continue
      
      key = line[:line.index('=')]
      if key not in _audio_metadata_fields_by_key:
        continue
      
      key = get_audio_metadata_field(key)
      value = line[line.index('=') + 1:len(line) - 1]
      data[key] = value
  else:
    lines = ffmpeg_output_from_conversion_to_mp3.replace('\r\n', '\n') \
                                                .replace('\r',   '\n') \
                                                .split('\n')
    
    for line in lines:
      re_match = _metadata_field_re.search(line)
      if re_match is None:
        continue
      
      key = None
      try:
        key = get_audio_metadata_field(re_match.group(1))
      except ValueError as e:
        if not str(e).startswith('unknown metadata field '):
          raise e
        
        continue
      
      if key in data and data[key] is not None:
        continue
      
      value = re_match.group(2)
      data[key] = value
  
  return AudioMetadata(data, verbose=verbose)