from api.dao.mysql_utils import get_cursor
from api.models.db_models import FileTypes, Catalog, Song
from api.models.factories.audio_metadata_factory import read_metadata
from api.models.factories.song_factory import build_song_from_metadata
from api.util.file_operations import get_file_contents, get_file_size_in_bytes, get_last_modified_timestamp
from api.util.functions import is_iterable
from api.util.logger import get_logger

import os

_artist_splitter_type_error = 'artist splitters must be an iterable collection of strings.'
_previously_scanned_file_names_type_error = 'previously scanned file names must be an iterable collection of strings.'
def get_songs_from_mp3s(catalog:Catalog, artist_splitters:list[str] = None, previously_scanned_file_names:set[str] = None) -> set[Song]:
  if artist_splitters is None:
    artist_splitters = [' featuring ', ' feat ', ' feat. ', ' ft ', ' ft. ', ' remixed by ', ' covered by ', ', ', ' vs ', ' vs. ', ' & ']
  elif not is_iterable(artist_splitters):
    raise TypeError(_artist_splitter_type_error)
  else:
    for splitter in artist_splitters:
      if not isinstance(splitter, str):
        raise TypeError(_artist_splitter_type_error)
  
  if previously_scanned_file_names is None:
    previously_scanned_file_names = set()
  elif not is_iterable(previously_scanned_file_names):
    raise TypeError(_previously_scanned_file_names_type_error)
  else:
    for fn in previously_scanned_file_names:
      if not isinstance(fn, str):
        raise TypeError(_previously_scanned_file_names_type_error)
  
  base_mp3_dir = catalog.get_base_mp3_dir()
  if not os.path.exists(base_mp3_dir):
    raise ValueError('couldn\'t find the mp3 directory "%s"; aborting scan.' % (base_mp3_dir,))
  
  logger = get_logger()
  result = set()
  for root, directories, files in os.walk(base_mp3_dir):
    logger.info('scanning directory "%s"...' % root)
    
    for file_name in files:
      full_name = '%s/%s' % (root, file_name)
      if file_name[len(file_name) - 4: len(file_name)] != '.mp3':
        logger.debug('')
        logger.info('the file "%s" isn\'t an mp3; skipping it.' % full_name)
        continue
      
      song_file_name = catalog.get_song_filename_from_full_filename(full_name)
      if song_file_name in previously_scanned_file_names:
        continue
      
      logger.debug('')
      logger.info('scanning file "%s"...' % full_name)
      with get_cursor(True) as cursor:
        query = 'SELECT begin_scan_get_last_updated(%s, "%s") AS last_scanned;' % (catalog.get_id(), song_file_name)
        cursor.execute(query)
        db_song_data = cursor.fetchone()
        if db_song_data is None:
          logger.error('got none for %s' % file_name)
        else:
          last_scanned = db_song_data['last_scanned']
          last_modified = get_last_modified_timestamp(full_name)
          
          logger.debug('last modified: %s' % last_modified)
          logger.debug('last scanned:  %s' % last_scanned)
          if last_scanned is not None and last_scanned > last_modified:
            logger.info('the file was scanned since its last modification; skipping it.')
            continue
      
      mp3_data = read_metadata(full_name)
      if mp3_data is None:
        logger.warn('got no metadata for "%s"; skipping it.' % (full_name,))
        continue
      
      logger.debug('found %s, which was modified at %s.' % (str(mp3_data), str(mp3_data.date_modified)))
      
      full_flac_file_name = '%s/%s' % (catalog.get_base_flac_dir(), mp3_data.filename[len(catalog.get_base_mp3_dir()):])
      if os.path.exists(full_flac_file_name):
        mp3_data.flac_file_size = get_file_size_in_bytes(full_flac_file_name)
      
      result.add(build_song_from_metadata(mp3_data, catalog, artist_splitters))
  
  return result

def get_mp3_contents(song:Song):
  return get_file_contents(song.get_full_filename(FileTypes.MP3))