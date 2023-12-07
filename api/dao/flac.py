from api.models.db_models import Catalog, Song
from api.models.factories.audio_metadata_factory import read_metadata
from api.models.factories.song_factory import build_song_from_metadata
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
      
      metadata                = read_metadata(orig_file_name)
      new_flac_file_name      = get_filename_from_song_title(metadata.title, 'flac')
      new_mp3_file_name       = '%s.mp3' % (new_flac_file_name[:-5], )
      new_full_flac_file_name = '%s/%s' % (root, new_flac_file_name)
      new_mp3_full_file_name  = '%s/%s' % (target_mp3_dir, new_mp3_file_name)
      
      print('original file: %s' % (orig_file_name, ))
      print('       (%s.)' % ('exists' if os.path.exists(orig_file_name) else 'doesn\'t exist', ))
      print('new flac file: %s' % (new_full_flac_file_name, ))
      print('       (%s.)' % ('exists' if os.path.exists(new_full_flac_file_name) else 'doesn\'t exist', ))
      print('     new file: %s' % (new_mp3_full_file_name, ))
      print('       (%s.)' % ('exists' if os.path.exists(new_mp3_full_file_name) else 'doesn\'t exist', ))
      print('')
      
      metadata.flac_exists = True
      result.append(build_song_from_metadata(metadata, catalog))
  
  return result
