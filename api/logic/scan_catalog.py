import os

import dao.catalog
import dao.mp3

from dao.song import save_song
from util.logger import get_logger
from models.factories.song_factory import build_song_from_mp3

def scan_catalog(catalog_name, is_id = False, artist_splitters = [' feat ', ' feat. ', ' featuring ', ' remixed by ', ', ', ' vs ', ' vs. ']):
  catalog = None
  if is_id:
    catalog_name = int(catalog_name)
    catalog = dao.catalog.get_catalog_by_id(catalog_name)
  else:
    catalog_name = str(catalog_name)
    catalog = dao.catalog.get_catalog_by_name(catalog_name)
  
  logger = get_logger()
  
  if not os.path.isdir(catalog.base_path):
    logger.error('the catalog\'s base path was "%s", which isn\'t a directory.' % catalog.base_path)
  
  logger.info('scanning %s...' % str(catalog))
  
  for (dirname, dirnames, filenames) in os.walk(catalog.base_path):
    logger.info('scanning directory "%s"...' % dirname)
    
    for filename in filenames:
      full_name = '%s/%s' % (dirname, filename)
      if filename[len(filename) - 4 : len(filename)] != '.mp3':
        logger.info('the file "%s" isn\'t an mp3; skipping it.' % full_name)
        continue
      
      logger.info('scanning file "%s"...' % full_name)
      mp3_data = dao.mp3.read_metadata(full_name)
      logger.debug('found %s, which was modified at %s.' % (str(mp3_data), str(mp3_data.date_modified)))
      
      song = build_song_from_mp3(mp3_data, catalog, artist_splitters)
      save_song(song)