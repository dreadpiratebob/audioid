from api.util.config import load_config
load_config('test')

from api.models.db_models import Catalog, Song, Album, SongAlbum
from api.models.factories.song_factory import build_song_from_metadata
from api.models.audio_metadata import AudioMetadata, AudioMetadataFields
from api.util.functions import get_search_text_from_raw_text

import unittest

class SongFactoryTests(unittest.TestCase):
  catalog = Catalog(None, 'debug', 'debug', 'debug', 'debug', '/thing/')
  mp3_with_diacritics_in_album_name = AudioMetadata({
    # required.
    AudioMetadataFields.FILENAME: '/thing/mp3/mp3.mp3', # make sure this starts with catalog._base_path (above).
    AudioMetadataFields.MP3_FILE_SIZE: 7,
    AudioMetadataFields.FLAC_FILE_SIZE: None,
    AudioMetadataFields.DATE_MODIFIED: 0,
    AudioMetadataFields.DURATION: 300.0,
    
    # for testing.
    AudioMetadataFields.ALBUM: 'Šiňě',
    AudioMetadataFields.TRACK: 2
  })
  
  def test_album_name_char_encoding(self):
    expected_album_lcase, expected_album_no_diacritics, expected_album_lcase_no_diacritics = \
      get_search_text_from_raw_text(self.mp3_with_diacritics_in_album_name.album)
    
    expected_album = Album(None, self.mp3_with_diacritics_in_album_name.album, expected_album_lcase, expected_album_no_diacritics, expected_album_lcase_no_diacritics, None)
    
    expected_filename = expected_title = self.mp3_with_diacritics_in_album_name.filename[len(self.catalog.get_base_path()) + 4:-4]
    expected = Song\
    (
      None,
      expected_title, expected_title, expected_title, expected_title,
      None, # year
      self.mp3_with_diacritics_in_album_name.duration,
      None,
      None,
      self.mp3_with_diacritics_in_album_name.mp3_file_size,
      self.mp3_with_diacritics_in_album_name.flac_file_size,
      expected_filename,
      self.mp3_with_diacritics_in_album_name.date_modified,
      self.catalog
    )
    
    expected.set_songs_albums([SongAlbum(expected, expected_album, 2)])
    
    actual = build_song_from_metadata(self.mp3_with_diacritics_in_album_name, self.catalog)
    
    self.assertEqual(expected, actual)

class DBModelEqualsAndHashTests(unittest.TestCase):
  catalog = Catalog(None, 'debug', 'debug', 'debug', 'debug', '/thing/')
  
  expected_basic_title = 'mp3.mp3'
  song_basic = Song(None, expected_basic_title, expected_basic_title, expected_basic_title, expected_basic_title,
                    None, # year
                    300.0, # duration
                    None, # title min age
                    None, # lyrics min age
                    2, # mp3 size
                    None, # flac size
                    expected_basic_title, # filename
                    0, # date modified
                    catalog)
  
  album = Album(None, 'Album!', 'album!', 'Album!', 'album!', None)
  song_with_album = Song(None, expected_basic_title, expected_basic_title, expected_basic_title, expected_basic_title,
                         None, # year
                         300.0, # duration
                         None,
                         None,
                         2,
                         None,
                         expected_basic_title, # filename
                         0, # date modified
                         catalog)
  
  def __init__(self, method_name:str = None):
    if method_name is None:
      super().__init__()
    else:
      super().__init__(method_name)
    
    self.song_with_album.set_songs_albums([SongAlbum(self.song_with_album, self.album, -1)])
  
  def test_basic_song_hash(self):
    actual1 = hash(self.song_basic)
    actual2 = hash(self.song_basic)
    self.assertEqual(actual1, actual2)
  
  def test_song_with_album_hash(self):
    actual1 = hash(self.song_with_album)
    actual2 = hash(self.song_with_album)
    self.assertEqual(actual1, actual2)

if __name__ == '__main__':
  unittest.main()