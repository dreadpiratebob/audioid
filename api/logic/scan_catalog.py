from api.dao.catalog import get_catalog
from api.dao.mysql_utils import get_cursor
from api.dao.mp3 import read_metadata
from api.dao.load_db_models import save_song
from api.util.logger import get_logger
from api.models.factories.song_factory import build_song_from_mp3

from api.util.file_operations import get_last_modified_timestamp
from api.util.functions import is_iterable

import os
import traceback

def scan_catalog(catalog_identifier, artist_splitters = None):
  if artist_splitters is None:
    artist_splitters = [' featuring ', ' feat ', ' feat. ', ' ft ', ' ft. ', ' remixed by ', ' covered by ', ', ', ' vs ', ' vs. ', ' & ']
  elif not is_iterable(artist_splitters):
    raise TypeError('artist splitters must be an iterable collection.')
  
  logger = get_logger()
  catalog = get_catalog(catalog_identifier)
  
  if not os.path.isdir(catalog.get_base_path()):
    logger.error('the catalog\'s base path was "%s", which isn\'t a directory.' % catalog.get_base_path())
  
  logger.info('scanning %s...' % str(catalog))
  
  for (dirname, dirnames, filenames) in os.walk(catalog.get_base_path()):
    logger.info('scanning directory "%s"...' % dirname)
    
    for filename in filenames:
      full_name = '%s/%s' % (dirname, filename)
      if filename[len(filename) - 4 : len(filename)] != '.mp3':
        logger.debug("")
        logger.info('the file "%s" isn\'t an mp3; skipping it.' % full_name)
        continue
      
      logger.debug("")
      logger.info('scanning file "%s"...' % full_name)
      with get_cursor(False) as cursor:
        sql_fn = full_name[len(catalog.get_base_path()):]
        query = 'SELECT last_scanned FROM songs WHERE filename = "%s"' % sql_fn
        cursor.execute(query)
        
        result = cursor.fetchone()
        if result is None:
          logger.error('got none for %s' % filename)
        else:
          last_scanned  = result['last_scanned']
          last_modified = get_last_modified_timestamp(full_name)
          
          logger.debug('last modified: %s' % last_modified)
          logger.debug('last scanned:  %s' % last_scanned)
          if last_scanned > last_modified:
            logger.info('the file was scanned since its last modification; skipping it.')
            continue
      
      mp3_data = read_metadata(full_name)
      if mp3_data is None:
        logger.warn('got no metadata for "%s"; skipping it.' % (full_name, ))
        continue
      
      logger.debug('found %s, which was modified at %s.' % (str(mp3_data), str(mp3_data.date_modified)))
      
      song = build_song_from_mp3(mp3_data, catalog, artist_splitters)
      try:
        save_song(song)
      except UnicodeEncodeError as e:
        raise e
      except Exception as e:
        logger.error('caught an exception of type %s: %s' % (str(type(e)), traceback.format_exc()))