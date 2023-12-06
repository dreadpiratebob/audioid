from api.models.db_models import Catalog, Song
from api.util.logger import Logger, get_logger
from api.util.file_operations import get_filename_from_song_title

import os

def get_songs_from_flacs(catalog:Catalog, base_flac_dir:str = None, base_mp3_dir:str = None, logger:Logger = get_logger()) -> list[Song]:
  if base_flac_dir is None:
    base_flac_dir = Catalog.get_base_flac_dir(catalog)
  
  if base_mp3_dir is None:
    base_mp3_dir = Catalog.get_base_mp3_dir(catalog)
  
  if not os.path.exists(base_flac_dir):
    return []
  
  result = []
  for root, dir_names, file_names in os.walk(base_flac_dir):
    logger.info('ingesting files from "%s"...' % (root,))
    
    target_mp3_dir = '%s%s' % (base_mp3_dir, root[len(base_flac_dir):])
    
    for file_name in file_names:
      extension = file_name[file_name.rfind('.') + 1:]
      
      orig_file_name = '%s/%s' % (root, file_name)
      if extension != 'flac':
        print('skipping "%s" because it\'s a %s file.' % (orig_file_name, extension))
      
      mp3_file_name  = '%s/%s' % (target_mp3_dir, file_name)
      
      print('original file: %s' % (orig_file_name, ))
      print('       (%s.)' % ('exists' if os.path.exists(orig_file_name) else 'doesn\'t exist', ))
      print('     new file: %s' % (mp3_file_name, ))
      print('       (%s.)' % ('exists' if os.path.exists(mp3_file_name) else 'doesn\'t exist', ))
      print('')
  
  return result
