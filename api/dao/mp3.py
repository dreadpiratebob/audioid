from api.models.mp3 import MP3
from api.models.mp3 import MP3Fields
from api.util.file_operations import get_last_modified_timestamp
from api.util.logger import get_logger

import os
import subprocess
import mutagen.mp3

def read_metadata(filename):
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
  data = \
  {
    MP3Fields.DATE_MODIFIED.value: get_last_modified_timestamp(filename),
    MP3Fields.FILENAME.value: filename,
    MP3Fields.DURATION.value: audio.info.length
  }
  
  for line in lines:
    if '=' not in line:
      continue
    
    key = line[0:line.index('=')]
    value = line[line.index('=')+1:len(line)-1]
    data[key] = value
  
  return MP3(data)