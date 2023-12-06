from api.util.functions import get_search_text_from_raw_text

import os
import stat

_filename_acceptable_punctuation = {'.', '-', '_', ' ', '(', ')', '[', ']', '{', '}', '\'', '"'}
def get_filename_from_song_title(song_title: str, extension: str) -> str:
  lcase, no_diacritics, lcase_no_diacritics = get_search_text_from_raw_text(song_title)
  lcase_no_diacritics_no_punctuation = ''
  
  for i in range(len(lcase_no_diacritics)):
    current = lcase_no_diacritics[i]
    
    if 'a' <= current <= 'z' or '0' <= current <= '9' or current in _filename_acceptable_punctuation:
      lcase_no_diacritics_no_punctuation += current
      continue
    
    lcase_no_diacritics_no_punctuation += '_'
  
  return '%s.%s' % (lcase_no_diacritics_no_punctuation, extension)

def get_last_modified_timestamp(filename:str) -> int:
  file_stats = os.stat(filename)
  return file_stats[stat.ST_MTIME]

def get_file_size_in_bytes(filename:str) -> int:
  return os.path.getsize(filename)