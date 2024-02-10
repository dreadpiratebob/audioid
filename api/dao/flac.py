from api.models.audio_metadata import AudioMetadata, dedup_audio_metadata
from api.models.db_models import FileTypes, Catalog, Song
from api.models.factories.audio_metadata_factory import read_metadata
from api.models.factories.song_factory import build_song_from_metadata
from api.util.logger import Logger, get_logger
from api.util.file_operations import get_file_contents, get_file_size_in_bytes, get_filename_from_song_title
from api.util.functions import get_type_name

from mutagen.mp3 import MP3
from subprocess import PIPE, run

import os

def _transcode_flac_to_mp3(original_file_name:str, new_file_name:str) -> AudioMetadata:
  cmd = 'ffmpeg -i %s -ab 320k -map_metadata 0 -id3v2_version 3 %s'.split(' ')
  
  cmd[2] = original_file_name
  cmd[-1] = new_file_name
  
  ffmpeg_output = run(cmd, stdout=PIPE, stderr=PIPE).stderr
  ffmpeg_output = str(ffmpeg_output).replace('\\r', '\r').replace('\\n', '\n')
  print('ffmpeg:\n' + ffmpeg_output)
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
        logger.debug('"%s" already exists; checking metadata.' % (orig_mp3__file_name, ))
        _check_mp3_metadata(orig_flac_file_name, orig_mp3__file_name)
        continue
      
      metadata = read_metadata(orig_flac_file_name)
      deduped_metadata = dedup_audio_metadata(metadata)
      get_logger().debug('metadata:\n%s\n' % (str(metadata), ))
      get_logger().debug('deduped:\n%s\n' % (str(deduped_metadata), ))
      
      new_file_name = get_filename_from_song_title(deduped_metadata.title)
      new_full_flac_file_name = '%s/%s.flac' % (root, new_file_name,)
      new_full_mp3__file_name = '%s/%s.mp3' % (target_mp3_dir, new_file_name,)
      
      if orig_flac_file_name != new_full_flac_file_name:
        os.rename(orig_flac_file_name, new_full_flac_file_name)
      
      if metadata != deduped_metadata:
        # |=*(|<1|\|6 windows bugs.
        write_tag_values(new_full_flac_file_name, deduped_metadata)
      
      if os.path.exists(new_full_mp3__file_name):
        logger.debug('"%s" already exists; skipping it.' % (new_full_flac_file_name, ))
        _check_mp3_metadata(new_full_flac_file_name, new_full_mp3__file_name)
        continue
      
      try:
        metadata = _transcode_flac_to_mp3(new_full_flac_file_name, new_full_mp3__file_name)
      except Exception as e:
        logger.error('transcoding "%s" to "%s" failed with this %s: %s' % (orig_flac_file_name, orig_mp3__file_name if new_full_mp3__file_name is None else new_full_mp3__file_name, get_type_name(e), str(e)))
        raise e
      
      logger.debug('transcoded "%s" to "%s"...' % (new_full_flac_file_name, new_full_mp3__file_name))

      mp3_data = MP3(new_full_mp3__file_name)
      
      metadata.duration = mp3_data.info.length
      metadata.mp3_file_size = get_file_size_in_bytes(new_full_mp3__file_name)
      result.add(build_song_from_metadata(metadata, catalog))
  
  return result

def _check_mp3_metadata(flac_file_name:str, mp3_file_name:str) -> None:
  flac_metadata = read_metadata(flac_file_name)
  mp3_metadata = read_metadata(mp3_file_name)
  
  if flac_metadata == mp3_metadata:
    return
  
  write_tag_values(flac_file_name, mp3_metadata)

def get_flac_contents(song:Song):
  return get_file_contents(song.get_full_filename(FileTypes.FLAC))

def write_tag_values(full_filename:str, mp3_metadata:AudioMetadata) -> None:
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
  
  update_cmd = ['metaflac'] + ['--remove-tag=%s' % (field, ) for field in fields] + [full_filename]
  get_logger().debug('running "%s"' % (' '.join(update_cmd), ))
  run(update_cmd, stdout=PIPE, stderr=PIPE)
  
  update_cmd = ['metaflac'] + ['--set-tag=%s=%s' % (field, fields[field]) for field in fields] + [full_filename]
  get_logger().debug('running "%s"' % (' '.join(update_cmd), ))
  run(update_cmd, stdout=PIPE, stderr=PIPE)