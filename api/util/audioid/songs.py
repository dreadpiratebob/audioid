from api.util.functions import parse_bool
from api.util.http import QueryParam
from api.util.response_list_modifiers import OrderByCol, OrderColName, OrderDirection, get_order_parser, parse_page_size

class GetSongsOrderColumns(OrderColName):
  SONG_TITLE = 'song_title', 'the song\'s title'
  SONG_YEAR  = 'song_year', 'the year the song was released'
  ARTIST_NAME = 'artist_name', 'the name of the song\'s artist. (if this was something like "Some Artist feat. Another Artist" in the original file, that whole string will be used for the sort order.)'
  ALBUM_NAME = 'album_name', 'the name of the album that the song is on'
  ALBUM_ARTIST_NAME = 'album_artist_name', 'the name of the song\'s album\'s artist'
  TRACK_NUMBER = 'track_number', 'the song\'s track number'
  GENRE_NAME = 'genre_name', 'the song\'s genre\'s name'

get_songs_order_columns_by_column_name = {col.column_name: col for col in GetSongsOrderColumns}
default_get_songs_order_by = \
[
  OrderByCol(GetSongsOrderColumns.ALBUM_ARTIST_NAME, OrderDirection.ASCENDING),
  OrderByCol(GetSongsOrderColumns.ALBUM_NAME,        OrderDirection.ASCENDING),
  OrderByCol(GetSongsOrderColumns.TRACK_NUMBER,      OrderDirection.ASCENDING)
]

class GetSongsQueryParams(QueryParam):
  ALBUM_ID    = 'album_id',    False, int, 'integer', 'an integer', None, 'the id of the album whose songs to get; only one of this and album_name can be set.'
  ALBUM_NAME  = 'album_name',  False, str, 'string',  'a string',   None, 'the name of the album whose songs to get; only one of this and album_id can be set.'
  ALBUM_NAME_HAS_WILDCARDS      = 'album_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if album_name isn\'t set, album_name_has_wildcards is ignored.  if album_name_has_wildcards is true, % and _ in album_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character; otherwise, % and _ will be treated as literals.'
  ALBUM_NAME_IS_CASE_SENSITIVE  = 'album_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if album_name isn\'t set, album_name_is_case_sensitive is ignored.  if album_name_is_case_sensitive is true, only albums whose names match album_name\'s case will be returned; otherwise, album\'s whose names match regardless of case will be returned.'
  ALBUM_NAME_MATCHES_DIACRITICS = 'album_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if album_name isn\'t set, album_name_matches_diacritics is ignored.  if album_name_matches_diacritics is true, letters in album_name will be matched exactly; otherwise, diacritics will be stripped out of both the albums\'s names and the album_name parameter, so "a" in the query parameter will match "ä", "à", "å", etc. in the album names.'
  FILTER_ON_NULL_ALBUM          = 'filter_on_null_album',          False, parse_bool, 'boolean', 'a boolean', False, 'if filter_on_null_album is true and no album is specified, this will only include songs without an album.  otherwise, it\'ll include songs regardless of album (or lack thereof).  if either of album_id or album_name is set, this will be ignored.'
  ALBUM_ARTIST_ID   = 'album_artist_id',    False, int, 'integer', 'an integer', None, 'the id of the artist who wrote the album whose songs to get; only one of this and album_artist_name can be set.  if neither of album_id and album_name are set, this will be ignored.'
  ALBUM_ARTIST_NAME = 'album_artist_name',  False, str, 'string',  'a string',   None, 'the name of the artist who wrote the album whose songs to get; only one of this and album_artist_id can be set.  if neither of album_id and album_name are set, this will be ignored.'
  ALBUM_ARTIST_NAME_HAS_WILDCARDS      = 'album_artist_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if album_artist_name isn\'t set, album_artist_name_has_wildcards is ignored.  if album_artist_name_has_wildcards is false, only songs whose album artist\'s name is exactly equal to album_artist_name will be returned; otherwise, % and _ in album_artist_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.'
  ALBUM_ARTIST_NAME_IS_CASE_SENSITIVE  = 'album_artist_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if album_artist_name isn\'t set, album_artist_name_is_case_sensitive is ignored.  if album_artist_name_is_case_sensitive is false, only songs whose album artist\'s name is exactly equal to album_artist_name will be returned; otherwise, tracks whose album artist\'s name match album_artis_name regardless of case will be returned.'
  ALBUM_ARTIST_NAME_MATCHES_DIACRITICS = 'album_artist_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if album_artist_name isn\'t set, album_artist_name_matches_diacritics is ignored.  if album_artist_name_matches_diacritics is false, only songs whose album artist\'s name\'s diacritics exactly match album_artist_name\'s will be returned; otherwise, diacritics will be stripped out of both the artist album names and the query parameter before any comparisons are made.'
  FILTER_ON_NULL_ALBUM_ARTIST          = 'filter_on_null_album_artist',          False, parse_bool, 'boolean', 'a boolean', False, 'if filter_on_null_album_artist is true and no album artist is specified, this will only include songs on albums without an album artist.  otherwise, it\'ll include albums regardless of album artist (or lack thereof).  if neither of album_id and album_name or if either of album_artist_id and album_artist_name is set, this will be ignored.'
  ARTIST_ID   = 'artist_id',   False, int, 'integer', 'an integer', None, 'the id of the artist whose songs to get; only one of this and artist_name can be set.'
  ARTIST_NAME = 'artist_name', False, str, 'string',  'a string',   None, 'the name of the artist whose songs to get; only one of this and artist_id can be set.'
  ARTIST_NAME_HAS_WILDCARDS      = 'artist_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if artist_name isn\'t set, artist_name_has_wildcards is ignored.  if artist_name_has_wildcards is true, % and _ in artist_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  otherwise, % and _ will be treated literally.'
  ARTIST_NAME_IS_CASE_SENSITIVE  = 'artist_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if artist_name isn\'t set, artist_name_is_case_sensitive is ignored.  if artist_name_is_case_sensitive is true, only songs whose artist\'s name exactly match artist_name will be returned; otherwise, songs whose artist\'s names match artist_name regardless of case will be matched.'
  ARTIST_NAME_MATCHES_DIACRITICS = 'artist_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if artist_name isn\'t set, artist_name_matches_diacritics is ignored.  if artist_name_matches_diacritics is true, only songs whose artist\'s name\'s diacritics exactly match those in artist_name will be returned; otherwise, diacritics will be stripped out of the artist name both in the query parameter and the song before any comparisons are made.'
  FILER_ON_NULL_ARTIST           = 'filter_on_null_artist',          False, parse_bool, 'boolean', 'a boolean', False, 'if filter_on_null_artist is true and no artist is specified, only songs that don\'t have an artist will be returned; if filter_on_null_artist is false and no artist is specified, songs will be returned regardless of whether they have an artist.'
  CATALOG_ID  = 'catalog_id',  True,  int, 'integer', 'an integer', None, 'the id of the catalog to retrieve songs from'
  GENRE_ID    = 'genre_id',    False, int, 'integer', 'an integer', None, 'the id of the genre whose songs to get; only one of this and genre_name can be set.'
  GENRE_NAME  = 'genre_name',  False, str, 'string',  'a string',   None, 'the name of the genre whose songs to get; only one of this and genre_id can be set.'
  GENRE_NAME_HAS_WILDCARDS      = 'genre_name_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if genre_name isn\'t set, genre_name_has_wildcards is ignored.  if genre_name_has_wildcards is true, % and _ in genre_name will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  otherwise, % and _ will be treated literally.'
  GENRE_NAME_IS_CASE_SENSITIVE  = 'genre_name_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if genre_name isn\'t set, genre_name_is_case_sensitive is ignored.  if genre_name_is_case_sensitive is true, only songs whose genre\'s name exactly match genre_name will be returned; otherwise, songs whose genre\'s names match genre_name regardless of case will be returned.'
  GENRE_NAME_MATCHES_DIACRITICS = 'genre_name_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if genre_name isn\'t set, genre_name_matches_diacritics is ignored.  if genre_name_matches_diacritics is true, only songs whose genre\'s name\'s diacritics match genre_name will be returned; otherwise, all diacritics will be stripped out before any comparison is done.'
  FILTER_ON_NULL_GENRE          = 'filter_on_null_genre',          False, parse_bool, 'boolean', 'a boolean', False, 'if filter_on_null_genre is true and no genre is specified, only songs that don\'t have a genre will be returned; if filter_on_null_genre is false and no genre is specified, songs will be returned regardless of whether they have a genre.'
  SONG_TITLE = 'song_title', False, str, 'string', 'a string', None, 'the title of the songs to get'
  SONG_TITLE_HAS_WILDCARDS      = 'song_title_has_wildcards',      False, parse_bool, 'boolean', 'a boolean', True,  'if song_title isn\'t set, song_title_has_wildcards is ignored.  if song_title_has_wildcards is true, % and _ in song_title will be treated as wildcards where % matches zero or more characters and _ matches exactly one character, but either % or _ can match any character.  if song_title_has_wildcards is false, % and _ will be treated literally.'
  SONG_TITLE_IS_CASE_SENSITIVE  = 'song_title_is_case_sensitive',  False, parse_bool, 'boolean', 'a boolean', False, 'if song_title isn\'t set, song_title_is_case_sensitive is ignored.  if song_title_is_case_sensitive is true, letters in song_title will be matched exactly; otherwise, they\'ll match letters regardless of case.'
  SONG_TITLE_MATCHES_DIACRITICS = 'song_title_matches_diacritics', False, parse_bool, 'boolean', 'a boolean', False, 'if song_title isn\'t set, song_title_matches_diacritics is ignored.  if song_title_matches_diacritics is true, letters in song_title will be matched exactly; otherwise, diacritics will be stripped out of both the song_title parameter and song\'s title, so "a" in the query parameter will match "ä", "à", "å", etc. in the song title.'
  SONG_YEAR = 'song_year', False, int, 'integer', 'an integer', None, 'the year of the songs to get'
  ORDER_BY    = 'order_by',    False, get_order_parser(GetSongsOrderColumns, get_songs_order_columns_by_column_name), 'a comma-separated list of song-columns/direction pairs', 'a comma-separated list of song-columns/direction pairs', default_get_songs_order_by, 'each song column name must be one of %s; each direction must be "ascending" or "descending".  (each of those is case-insensitive.)' % (', '.join([col.column_name for col in GetSongsOrderColumns]), )
  PAGE_NUMBER = 'page_number', False, int, 'integer', 'an integer', 1, 'the 1-based number of which page to get; e.g. if you\'re getting 50 results at a time and you want results #51-100, this would be 2.'
  PAGE_SIZE   = 'page_size',   False, parse_page_size, 'integer', 'an integer', 100, 'the size of one page; i.e. the maximum number of results to get.  if this is "all", all results will be returned regardless of what the value of page_number is.'