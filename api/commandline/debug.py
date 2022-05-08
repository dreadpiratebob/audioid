import sys
sys.path.insert(1, '../')

from dao.mp3 import read_metadata
from models.catalog import Catalog
from models.factories.song_factory import build_song_from_mp3

mp3_data = read_metadata('/mnt/data/heinrich/audioid_debug/ghost/prequelle/rats.mp3')
print('year: ' + str(mp3_data.year))

catalog = Catalog(1, 'debug', '/mnt/data/heinrich/audioid_debug')
song = build_song_from_mp3(mp3_data, catalog, [])

print(str(song))