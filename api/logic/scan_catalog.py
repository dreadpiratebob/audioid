from api.dao.flac import get_songs_from_flacs
from api.dao.load_db_models import get_catalog, save_song
from api.dao.mp3 import get_songs_from_mp3s
from api.dao.mysql_utils import get_cursor
from api.models.audio_metadata import AudioMetadata
from api.models.db_models import Catalog, Song
from api.models.factories.audio_metadata_factory import read_metadata
from api.models.factories.song_factory import build_song_from_metadata
from api.util.file_operations import get_filename_from_song_title
from api.util.functions import get_type_name
from api.util.logger import get_logger

from pymysql.err import OperationalError
from subprocess import run, PIPE

import os
import traceback

def _copy_tag_values(flac_filename:str, mp3_metadata:AudioMetadata) -> str:
  fields = {'title': mp3_metadata.title}
  
  if mp3_metadata.artist is not None:
    fields['artist'] = mp3_metadata.artist
  
  if mp3_metadata.album_artist is not None:
    fields['album_artist'] = mp3_metadata.album_artist
  
  if mp3_metadata.album is not None:
    fields['album'] = mp3_metadata.album
  
  if mp3_metadata.track is not None:
    fields['track'] = mp3_metadata.track
  
  if mp3_metadata.genre is not None:
    fields['genre'] = mp3_metadata.genre
  
  if mp3_metadata.year is not None:
    fields['year'] = mp3_metadata.year
  
  if mp3_metadata.comment is None:
    fields['comment'] = ''
  else:
    fields['comment'] = mp3_metadata.comment
  
  update_cmd = ['metaflac'] + ['--set-tag=%s=%s' % (field, fields[field]) for field in fields] + [flac_filename]
  get_logger().debug('running "%s"' % (' '.join(update_cmd), ))
  
  result = run(update_cmd, stdout=PIPE, stderr=PIPE)
  
  get_logger().debug('got a %s:' % (get_type_name(result)))
  print(result)

def _fix_metadata(catalog:Catalog) -> set[Song]:
  base_bork_dir = catalog.get_base_broken_metadata_dir()
  if not os.path.exists(base_bork_dir):
    return set()
  
  base_mp3_dir = catalog.get_base_mp3_dir()
  result = set()
  for root, directories, files in os.walk(base_bork_dir):
    source_mp3_dir = '%s%s' % (base_mp3_dir, root[len(base_bork_dir):])
    
    for file in files:
      full_filename = '%s/%s' % (root, file)
      mp3_file_name = '%s/%s' % (source_mp3_dir, file.lower())
      
      if not '.' in file:
        get_logger().debug('the file "%s" doesn\'t have an extension; skipping it.' % (full_filename, ))
        if not os.path.exists(mp3_file_name):
          run(['cp', full_filename, mp3_file_name])
        
        continue
      
      extension = file[file.rfind('.') + 1:]
      if extension != 'flac':
        get_logger().debug('the file "%s" is a %s file, not a flac file; skipping it.' % (full_filename, extension))
        if not os.path.exists(mp3_file_name):
          run(['cp', full_filename, mp3_file_name])
        
        continue
      
      get_logger().debug('attempting to fix metadata for "%s"...' % (full_filename, ))
      flac_metadata = read_metadata(full_filename)
      fixed_filename = get_filename_from_song_title(flac_metadata.title)
      new_fix_metadata_filename = '%s/%s.%s'  % (root, fixed_filename, extension)
      full_mp3_filename = '%s/%s.mp3' % (source_mp3_dir, fixed_filename)
      
      print(' full filename: ' + full_filename)
      print('fixed filename: ' + fixed_filename)
      
      if new_fix_metadata_filename != full_filename:
        run(['mv', full_filename, new_fix_metadata_filename])
        full_filename = new_fix_metadata_filename
      
      if not os.path.exists(full_mp3_filename):
        get_logger().warn('no mp3 equivalent was found for "%s".' % (full_filename, ))
        continue
      
      mp3_metadata = read_metadata(full_mp3_filename)
      mp3_metadata.flac_exists = True
      
      _copy_tag_values(full_filename, mp3_metadata)
      catalog.get_base_flac_dir()
      
      new_flac_filename = '%s%s' % (catalog.get_base_flac_dir(), full_filename[len(catalog.get_base_broken_metadata_dir()):])
      run(['mv', new_fix_metadata_filename, new_flac_filename])
      
      result.add(build_song_from_metadata(mp3_metadata, catalog))
  
  return result

def scan_catalog(catalog_identifier:[int, str], artist_splitters = None) -> None:
  logger = get_logger()
  catalog = get_catalog(catalog_identifier, True)
  
  if not os.path.isdir(catalog.get_base_path()):
    logger.error('the catalog\'s base path was "%s", which isn\'t a directory.' % catalog.get_base_path())
  
  logger.info('scanning %s...' % str(catalog))
  
  flac_songs      = get_songs_from_flacs(catalog, logger)
  flac_file_names = set([s.get_filename() for s in flac_songs])
  
  fixed_songs      = _fix_metadata(catalog)
  fixed_file_names = set([s.get_filename() for s in fixed_songs])
  
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