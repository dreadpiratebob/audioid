import os
import stat

def get_last_modified_timestamp(filename):
  file_stats = os.stat(filename)
  return file_stats[stat.ST_MTIME]