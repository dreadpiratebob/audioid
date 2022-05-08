import os
import subprocess

from models.mp3 import MP3
from models.mp3 import MP3Fields
from util.logger import get_logger
from util.file_operations import get_last_modified_timestamp

def read_metadata(filename):
  outputfile = '%s metadata.txt' % filename
  subprocess.run(['ffmpeg', '-i', filename, '-f', 'ffmetadata', outputfile], capture_output=True)
  
  lines = []
  with open(outputfile) as f:
    lines = f.readlines()
  
  os.remove(outputfile)
  
  data = \
  {
    MP3Fields.DATE_MODIFIED.value: get_last_modified_timestamp(filename),
    MP3Fields.FILENAME.value: filename
  }
  
  for line in lines:
    if '=' not in line:
      continue
    
    key = line[0:line.index('=')]
    value = line[line.index('=')+1:len(line)-1]
    data[key] = value
  
  return MP3(data)