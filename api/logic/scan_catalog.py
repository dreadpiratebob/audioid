from api.dao.flac import get_songs_from_flacs
from api.dao.load_db_models import get_catalog, save_song
from api.models.factories.audio_metadata_factory import read_metadata
from api.dao.mysql_utils import get_cursor
from api.models.factories.song_factory import build_song_from_mp3
from api.util.file_operations import get_base_flac_dir, get_base_mp3_dir, get_last_modified_timestamp
from api.util.functions import is_iterable
from api.util.logger import get_logger

from pymysql.err import OperationalError
import os
import traceback

def scan_catalog(catalog_identifier:[int, str], artist_splitters = None) -> None:
  if artist_splitters is None:
    artist_splitters = [' featuring ', ' feat ', ' feat. ', ' ft ', ' ft. ', ' remixed by ', ' covered by ', ', ', ' vs ', ' vs. ', ' & ']
  elif not is_iterable(artist_splitters):
    raise TypeError('artist splitters must be an iterable collection.')
  
  logger = get_logger()
  catalog = get_catalog(catalog_identifier, True)
  
  if not os.path.isdir(catalog.get_base_path()):
    logger.error('the catalog\'s base path was "%s", which isn\'t a directory.' % catalog.get_base_path())
  
  logger.info('scanning %s...' % str(catalog))
  
  base_flac_dir   = catalog.get_base_flac_dir()
  base_mp3_dir    = catalog.get_base_mp3_dir()
  flac_songs      = get_songs_from_flacs(catalog, base_flac_dir, base_mp3_dir, logger)
  flac_file_names = set([s.get_filename() for s in flac_songs])
  
  if not os.path.exists(base_mp3_dir):
    raise ValueError('couldn\'t find the mp3 directory "%s"; aborting scan.' % (base_mp3_dir, ))
  
  with get_cursor(True) as cursor:
    cursor.execute('UPDATE songs SET mp3_exists=0 WHERE catalog_id=%s' % (str(catalog.get_id()), ))
  
  for (dir_name, dir_names, file_names) in os.walk(base_mp3_dir):
    logger.info('scanning directory "%s"...' % dir_name)
    
    for filename in file_names:
      full_name = '%s/%s' % (dir_name, filename)
      if filename[len(filename) - 4 : len(filename)] != '.mp3':
        logger.debug('')
        logger.info('the file "%s" isn\'t an mp3; skipping it.' % full_name)
        continue
      
      logger.debug('')
      logger.info('scanning file "%s"...' % full_name)
      with get_cursor(True) as cursor:
        sql_fn = catalog.get_song_filename_from_full_filename(full_name)
        query = 'SELECT begin_scan_get_last_updated(%s, "%s") AS last_scanned;' % (catalog.get_id(), sql_fn)
        cursor.execute(query)
        result = cursor.fetchone()
        if result is None:
          logger.error('got none for %s' % filename)
        else:
          last_scanned  = result['last_scanned']
          last_modified = get_last_modified_timestamp(full_name)
          
          logger.debug('last modified: %s' % last_modified)
          logger.debug('last scanned:  %s' % last_scanned)
          if last_scanned is not None and last_scanned > last_modified:
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
      except OperationalError as e:
        logger.error('caught a mysql error: %s' % (str(e), ))
      except Exception as e:
        logger.error('caught an exception of type %s: %s' % (str(type(e)), traceback.format_exc()))
  
  with get_cursor(True) as cursor:
    cursor.execute('CALL delete_songs_without_mp3s(%s);' % (str(catalog.get_id(), )))
    cursor.execute('CALL clean_unused_data();')