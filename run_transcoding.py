from api.dao.flac import get_songs_from_flacs
from api.models.db_models import Catalog

catalog = Catalog(4, 'debug', 'debug', 'debug', 'debug', '/music')

result = get_songs_from_flacs(catalog)

print()
print()
print('found %s songs.' % (len(result), ))
for song in result:
  flac_message = 'no flac' if song.get_flac_file_size_in_bytes() is None else ('%s Mb flac' % (song.get_flac_file_size_in_bytes(), ))
  print('  • %s (%s Mb mp3; %s)' % (str(song), song.get_mp3_file_size_in_bytes()/1024/1024, flac_message))