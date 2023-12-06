from api.dao.flac import get_songs_from_flacs
from api.models.db_models import Catalog

catalog = Catalog(4, 'debug', 'debug', 'debug', 'debug', '/music')

get_songs_from_flacs(catalog)