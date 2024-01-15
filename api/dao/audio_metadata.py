from api.models.audio_metadata import AudioMetadata
from api.util.logger import get_logger

from subprocess import run, PIPE

def write_tag_values(full_filename:str, mp3_metadata:AudioMetadata) -> str:
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
  
  update_cmd = ['metaflac'] + ['--set-tag=%s=%s' % (field, fields[field]) for field in fields] + [full_filename]
  get_logger().debug('running "%s"' % (' '.join(update_cmd), ))
  
  run(update_cmd, stdout=PIPE, stderr=PIPE)
