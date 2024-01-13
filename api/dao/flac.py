from api.models.audio_metadata import AudioMetadata
from api.models.db_models import FileTypes, Catalog, Song
from api.models.factories.audio_metadata_factory import read_metadata
from api.models.factories.song_factory import build_song_from_metadata
from api.util.logger import Logger, get_logger
from api.util.file_operations import get_file_contents, get_file_size_in_bytes, get_filename_from_song_title
from api.util.functions import get_type_name

from mutagen.mp3 import MP3

import os

from subprocess import PIPE, run

def _transcode_flac_to_mp3(original_file_name:str, new_file_name:str) -> AudioMetadata:
  cmd = 'ffmpeg -i %s -ab 320k -map_metadata 0 -id3v2_version 3 %s'.split(' ')
  
  cmd[2] = original_file_name
  cmd[-1] = new_file_name
  
  ffmpeg_output = run(cmd, stdout=PIPE, stderr=PIPE).stderr
  ffmpeg_output = str(ffmpeg_output).replace('\\r', '\r').replace('\\n', '\n')
  
  return read_metadata(new_file_name, ffmpeg_output)

def get_songs_from_flacs(catalog:Catalog, logger:Logger = get_logger()) -> set[Song]:
  base_flac_dir = catalog.get_base_flac_dir()
  base_mp3_dir  = catalog.get_base_mp3_dir()
  
  if not os.path.exists(base_flac_dir):
    return set()
  
  result = set()
  for root, dir_names, file_names in os.walk(base_flac_dir):
    logger.info('ingesting files from "%s"...' % (root,))
    
    target_mp3_dir = '%s%s' % (base_mp3_dir, root[len(base_flac_dir):].lower())
    if not os.path.exists(target_mp3_dir):
      os.makedirs(target_mp3_dir)
    
    for file_name in file_names:
      extension = file_name[file_name.rfind('.') + 1:]
      
      orig_flac_file_name = '%s/%s' % (root, file_name)
      if extension != 'flac':
        target_file_name = '%s/%s' % (target_mp3_dir, file_name.lower())
        if not os.path.exists(target_file_name):
          logger.debug('"%s" is missing "%s"; copying it over.')
          run(['cp', orig_flac_file_name, target_file_name])
        
        logger.debug('not transcoding "%s" because it\'s a %s file.' % (orig_flac_file_name, extension))
        continue
      
      orig_mp3__file_name = '%s/%smp3' % (target_mp3_dir, file_name[:-4])
      if os.path.exists(orig_mp3__file_name):
        logger.debug('"%s" already exists; skipping it.' % (orig_mp3__file_name, ))
        continue
      
      new_full_mp3__file_name = None
      try:
        metadata                = _transcode_flac_to_mp3(orig_flac_file_name, orig_mp3__file_name)
        new_file_name           = get_filename_from_song_title(metadata.title)
        new_flac_file_name      = '%s.flac' % (new_file_name, )
        new_mp3__file_name      = '%s.mp3'  % (new_file_name, )
        new_full_flac_file_name = '%s/%s' % (root, new_flac_file_name)
        new_full_mp3__file_name = '%s/%s' % (target_mp3_dir, new_mp3__file_name)
        
        if orig_flac_file_name != new_full_flac_file_name:
          run(['mv', orig_flac_file_name, new_full_flac_file_name])
        
        if orig_mp3__file_name != new_full_mp3__file_name:
          run(['mv', orig_mp3__file_name, new_full_mp3__file_name])
      except Exception as e:
        logger.error('transcoding "%s" to "%s" failed with this %s: %s' % (orig_flac_file_name, orig_mp3__file_name if new_full_mp3__file_name is None else new_full_mp3__file_name, get_type_name(e), str(e)))
        raise e
      
      logger.debug('transcoded "%s" to "%s"...' % (new_full_flac_file_name, new_full_mp3__file_name))

      mp3_data = MP3(new_full_mp3__file_name)
      
      metadata.duration = mp3_data.info.length
      metadata.mp3_file_size = get_file_size_in_bytes(new_full_mp3__file_name)
      result.add(build_song_from_metadata(metadata, catalog))
  
  return result

def get_flac_contents(song:Song):
  return get_file_contents(song.get_full_filename(FileTypes.FLAC))