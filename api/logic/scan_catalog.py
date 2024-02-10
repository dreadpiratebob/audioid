from api.dao.flac import get_songs_from_flacs, write_tag_values
from api.dao.load_db_models import get_catalog, save_song
from api.dao.mp3 import get_songs_from_mp3s
from api.dao.mysql_utils import get_cursor
from api.models.db_models import Catalog, Song
from api.models.factories.audio_metadata_factory import read_metadata
from api.models.factories.song_factory import build_song_from_metadata
from api.util.file_operations import get_file_size_in_bytes, get_filename_from_song_title
from api.util.logger import get_logger

from pathlib import Path
from pymysql.err import OperationalError
from subprocess import run

import os
import traceback

def _fix_metadata(catalog:Catalog) -> set[Song]:
  base_bork_dir = catalog.get_base_broken_metadata_dir()
  if not os.path.exists(base_bork_dir):
    return set()
  
  base_mp3_dir = catalog.get_base_mp3_dir()
  result = set()
  for root, directories, files in os.walk(base_bork_dir):
    source_mp3_dir = '%s%s' % (base_mp3_dir, root[len(base_bork_dir):])
    
    if len(os.listdir(root)) == 0:
      os.rmdir(root)
      continue
    
    for directory in directories:
      full_dir_name = '%s/%s' % (root.replace('\\', '/'), directory)
      if len(os.listdir(full_dir_name)) == 0:
        os.rmdir(full_dir_name)
    
    for file in files:
      full_filename = '%s/%s' % (root, file)
      mp3_file_name = '%s/%s' % (source_mp3_dir, file.lower())
      
      if '.' not in file:
        get_logger().debug('the file "%s" doesn\'t have an extension; skipping it.' % (full_filename, ))
        if not os.path.exists(mp3_file_name):
          run(['cp', full_filename, mp3_file_name])
        
        continue
      
      extension = file[file.rfind('.') + 1:]
      if extension != 'flac':
        get_logger().debug('the file "%s" is a %s file, not a flac file; skipping it.' % (full_filename, extension))
        if not os.path.exists(mp3_file_name):
          run(['cp', full_filename, mp3_file_name])
        os.remove(full_filename)
        
        continue
      
      get_logger().debug('attempting to fix metadata for "%s"...' % (full_filename, ))
      
      flac_metadata = read_metadata(full_filename)
      title_pieces  = flac_metadata.title.split('\\;')
      use_first     = True
      test_val      = title_pieces[0]
      for i in range(1, len(title_pieces)):
        if title_pieces[i] != test_val:
          use_first = False
          break
      
      if use_first:
        flac_metadata.title = title_pieces[0]
      
      fixed_filename = get_filename_from_song_title(flac_metadata.title)
      new_fix_metadata_filename = '%s/%s.%s'  % (root, fixed_filename, extension)
      full_mp3_filename = '%s/%s.mp3' % (source_mp3_dir, fixed_filename)
      
      get_logger().debug('         title: ' + flac_metadata.title)
      get_logger().debug('fixed filename: ' + fixed_filename)
      get_logger().debug(' full filename: ' + full_filename)
      
      if new_fix_metadata_filename != full_filename:
        run(['mv', full_filename, new_fix_metadata_filename])
        full_filename = new_fix_metadata_filename
      
      if not os.path.exists(full_mp3_filename):
        get_logger().warn('no mp3 equivalent was found for "%s".' % (full_filename, ))
        get_logger().debug('                          looking here: "%s"' % (full_mp3_filename, ))
        continue
      
      mp3_metadata = read_metadata(full_mp3_filename)
      mp3_metadata.mp3_file_size = get_file_size_in_bytes(full_mp3_filename)
      
      write_tag_values(full_filename, mp3_metadata)
      catalog.get_base_flac_dir()
      
      new_flac_filename = '%s%s' % (catalog.get_base_flac_dir(), full_filename[len(catalog.get_base_broken_metadata_dir()):])
      new_flac_filename = new_flac_filename.replace('\\', '/')
      os.makedirs(new_flac_filename[:new_flac_filename.rfind('/')], exist_ok=True)
      get_logger().debug('moving the file to "%s"...' % (new_flac_filename, ))
      os.rename(new_fix_metadata_filename, new_flac_filename)
      
      result.add(build_song_from_metadata(mp3_metadata, catalog))
  
  for _root, _directories, _files in os.walk(base_bork_dir, topdown=False):
    if len(_files) > 0 or len(_directories) > 0:
      continue
    
    path = Path(_root)
    path.rmdir()
  
  return result

def scan_catalog(catalog_identifier:[int, str], artist_splitters = None) -> None:
  logger = get_logger()
  catalog = get_catalog(catalog_identifier, True)
  
  if not os.path.isdir(catalog.get_base_path()):
    logger.error('the catalog\'s base path was "%s", which isn\'t a directory.' % catalog.get_base_path())
  
  logger.info('scanning %s...' % str(catalog))
  
  flac_songs      = get_songs_from_flacs(catalog, logger)
  flac_file_names = {s.get_filename() for s in flac_songs}
  
  fixed_songs      = _fix_metadata(catalog)
  fixed_file_names = {s.get_filename() for s in fixed_songs}
  
  mp3_songs = get_songs_from_mp3s(catalog, artist_splitters, flac_file_names | fixed_file_names)
  
  with get_cursor(True) as cursor:
    cursor.execute('UPDATE songs SET mp3_exists=0 WHERE catalog_id=%s' % (str(catalog.get_id()), ))
  
  for song in flac_songs | fixed_songs | mp3_songs:
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