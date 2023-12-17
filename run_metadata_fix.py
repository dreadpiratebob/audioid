from api.logic.scan_catalog import _fix_metadata
from api.models.db_models import Catalog

catalog = Catalog(4, 'debug', 'debug', 'debug', 'debug', '/music')

result = _fix_metadata(catalog)

print()
print()
print('found %s songs.' % (len(result), ))
for song in result:
  print('  • %s' % (str(song), ))