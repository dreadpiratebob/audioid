from api.models.audio_metadata import AudioMetadataFields, AudioMetadata
from api.util.file_operations import get_file_size_in_bytes, get_last_modified_timestamp
from api.util.logger import get_logger

import mutagen.mp3
import os
import subprocess

_bad_filename_error_message = 'metadata can only be read from files with either an mp3 or flac extension.'
def read_metadata(filename:str) -> AudioMetadata:
  if not '.' in filename:
    raise ValueError(_bad_filename_error_message)
  
  extension = filename[filename.rfind('.') + 1:]
  if extension != 'mp3' and extension != 'flac':
    raise ValueError(_bad_filename_error_message)
  
  # ffmpeg -i filename -f ffmetadata outputfile
  outputfile = '%s metadata.txt' % filename
  subprocess.run(['ffmpeg', '-i', filename, '-f', 'ffmetadata', outputfile], capture_output=True)
  
  if not os.path.exists(outputfile):
    get_logger().error('ffmpeg failed for "%s".' % (str(filename), ))
    return None
  
  lines = []
  with open(outputfile) as f:
    lines = f.readlines()
  
  os.remove(outputfile)
  
  audio = mutagen.mp3.MP3(filename)
  file_size = get_file_size_in_bytes(filename)
  data = \
  {
    AudioMetadataFields.DATE_MODIFIED.field_name: get_last_modified_timestamp(filename),
    AudioMetadataFields.FILENAME.field_name: filename,
    AudioMetadataFields.DURATION.field_name: audio.info.length,
    AudioMetadataFields.FILE_SIZE.field_name: file_size
  }
  
  for line in lines:
    if '=' not in line:
      continue
    
    key = line[:line.index('=')]
    value = line[line.index('=')+1:len(line)-1]
    data[key] = value
  
  return AudioMetadata(data)
