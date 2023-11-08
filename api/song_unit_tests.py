from api.util.config import load_config
load_config('test')

from api.models.db_models import Catalog, Song, Album, SongAlbum
from api.models.factories.song_factory import build_song_from_mp3
from api.models.mp3 import MP3, MP3Fields
from api.util.functions import get_search_text_from_raw_text

import unittest

class SongFactoryTests(unittest.TestCase):
  catalog = Catalog(None, 'debug', '/')
  mp3_with_diacritics_in_album_name = MP3({
    # required.
    MP3Fields.FILENAME.value: 'mp3.mp3',
    MP3Fields.DATE_MODIFIED.value: 0,
    MP3Fields.DURATION.value: 300.0,
    
    # for testing.
    MP3Fields.ALBUM.value: 'Šiňě',
    MP3Fields.TRACK.value: 2
  })
  
  def test_album_name_char_encoding(self):
    expected_album_lcase, expected_album_no_diacritics, expected_album_lcase_no_diacritics = \
      get_search_text_from_raw_text(self.mp3_with_diacritics_in_album_name.album)
    
    album = Album(None, self.mp3_with_diacritics_in_album_name.album, expected_album_lcase, expected_album_no_diacritics, expected_album_lcase_no_diacritics, None)
    
    expected = Song\
    (
      None,
      self.mp3_with_diacritics_in_album_name.filename, self.mp3_with_diacritics_in_album_name.filename, self.mp3_with_diacritics_in_album_name.filename, self.mp3_with_diacritics_in_album_name.filename,
      None, # year
      self.mp3_with_diacritics_in_album_name.duration,
      self.mp3_with_diacritics_in_album_name.filename,
      self.mp3_with_diacritics_in_album_name.date_modified,
      self.catalog
    )
    
    expected.set_songs_albums([SongAlbum(expected, album, 2)])
    
    actual = build_song_from_mp3(self.mp3_with_diacritics_in_album_name, self.catalog)
    
    self.assertEqual(expected, actual)

if __name__ == '__main__':
  unittest.main()