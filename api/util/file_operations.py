from api.util.functions import get_search_text_from_raw_text, get_type_name

from enum import Enum
import os
import stat

class AudioFileTypes(Enum):
  FLAC = 'flac'
  MP3  = 'mp3'

_filename_acceptable_punctuation = {'.', '-', '_', ' ', '(', ')', '[', ']', '{', '}', '\'', '"'}
def get_filename_from_song_title(song_title:str) -> str:
  input_text = '' + song_title
  
  lcase, no_diacritics, lcase_no_diacritics = get_search_text_from_raw_text(input_text)
  lcase_no_diacritics_no_punctuation = ''
  
  for i in range(len(lcase_no_diacritics)):
    current = lcase_no_diacritics[i]
    
    if 'a' <= current <= 'z' or '0' <= current <= '9' or current in _filename_acceptable_punctuation:
      lcase_no_diacritics_no_punctuation += current
      continue
    
    lcase_no_diacritics_no_punctuation += '_'
  
  return lcase_no_diacritics_no_punctuation

def get_last_modified_timestamp(filename:str) -> int:
  file_stats = os.stat(filename)
  return file_stats[stat.ST_MTIME]

def get_file_size_in_bytes(filename:str) -> int:
  return os.path.getsize(filename)

def get_file_contents(filename:str, stream:bool = False) -> bytes:
  if not isinstance(filename, str):
    raise TypeError('a filename must be a string; found "%s", which is a %s, instead.' % (filename, get_type_name(filename)))
  
  if not os.path.exists(filename):
    raise ValueError('no file named "%s" exists.' % (filename, ))
  
  result = bytes()
  
  with open(filename, 'rb') as file:
    while True:
      chunk = file.read()
      if not chunk:
        break
      
      if stream:
        yield chunk
      else:
        result += chunk
  
  if not stream:
    return result