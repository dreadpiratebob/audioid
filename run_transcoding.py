from api.dao.flac import get_songs_from_flacs
from api.models.db_models import Catalog

catalog = Catalog(4, 'debug', 'debug', 'debug', 'debug', '/music')

result = get_songs_from_flacs(catalog)

print()
print()
print('found %s songs.' % (len(result), ))
for song in result:
  print(str(song))