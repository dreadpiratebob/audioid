from api.dao.mysql_utils import commit, get_cursor
from api.exceptions.http_base import NotImplementedException
from api.exceptions.song_data import InvalidCountException, InvalidSongDataException
from api.models.db_models import Catalog, Album, Artist, Genre, Song, SongAlbum, SongArtist
from api.util.audioid.artists import GetArtistsOrderColumns, IncludeAlbumModes, default_get_artists_order_by
from api.util.audioid.catalogs import GetCatalogsOrderColumns, default_get_catalogs_order_by
from api.util.audioid.genres import GetGenresOrderColumns, default_get_genres_order_by
from api.util.audioid.songs import GetSongsOrderColumns, default_get_songs_order_by
from api.util.functions import get_search_text_from_raw_text, get_type_name
from api.util.logger import get_logger
from api.util.response_list_modifiers import \
  FilterInfo, default_filter_info, \
  OrderByCol, PageInfo, \
  OrderDirection, get_order_clause

invalid_catalog_id_error = 'a catalog id must be a nonnegative int.'
invalid_artist_id_error = 'an artist id must be a nonnegative int.'
invalid_album_id_error = 'an album id must be a nonnegative int.'
invalid_album_artist_id_error = 'an album artist id must be a nonnegative int.'

genres = dict()

_name_columns = \
{
  (True,  True ): ('title', 'name'),
  (False, True ): ('lcase_title', 'lcase_name'),
  (True,  False): ('no_diacritic_title', 'no_diacritic_name'),
  (False, False): ('lcase_no_diacritic_title', 'lcase_no_diacritic_name')
}

def get_catalog(catalog_identifier:[int, str], include_base_path:bool = False) -> Catalog:
  catalog_filter = FilterInfo(None, None, False, True, True, False)
  
  if isinstance(catalog_identifier, int):
    catalog_filter.id = catalog_identifier
  elif isinstance(catalog_identifier, str):
    catalog_filter.name = catalog_identifier
  else:
    raise TypeError('a catalog identifier must be an int (a catalog id) or a string (a catalog name).')
  
  result = get_catalogs(catalog_filter, include_base_paths=include_base_path)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  search_type = 'id'
  if isinstance(catalog_identifier, str):
    search_type = 'name'
  
  raise ValueError('%s catalogs were found with the %s "%s".' % (len(result), search_type, catalog_identifier))

get_catalogs_order_by_type_error = 'order_by for getting catalogs must be a list of catalog columns.'
def get_catalogs(catalog_filter:FilterInfo = None, order_by:list[OrderByCol] = None, page_info:PageInfo = None, include_base_paths:bool = False) -> list[Catalog]:
  if catalog_filter is None:
    catalog_filter = default_filter_info
  elif not isinstance(catalog_filter, FilterInfo):
    raise TypeError('a catalog filter must be filter info.')
  
  if order_by is None:
    order_by = default_get_catalogs_order_by
  elif isinstance(order_by, (list, tuple)):
    if len(order_by) == 0:
      order_by = default_get_catalogs_order_by
    else:
      for ob in order_by:
        if not isinstance(ob, OrderByCol) or not isinstance(ob.col, GetCatalogsOrderColumns):
          raise TypeError(get_catalogs_order_by_type_error)
  else:
    raise TypeError(get_catalogs_order_by_type_error)
  
  if page_info is not None and not isinstance(page_info, PageInfo):
    raise TypeError('invalid page info for getting catalogs.')
  
  if not isinstance(include_base_paths, bool):
    raise TypeError('the "include base paths" for catalogs must be a bool.')
  
  catalogs_select   = 'SELECT\n' \
                      '  c.id AS catalog_id,\n' \
                      '  c.name AS catalog_name,\n' \
                      '  c.lcase_name AS catalog_lcase_name,\n' \
                      '  c.no_diacritic_name AS catalog_no_diacritic_name,\n' \
                      '  c.lcase_no_diacritic_name AS catalog_lcase_no_diacritic_name,\n' \
                      '  c.base_path AS catalog_base_path\n'
  catalogs_from     = 'FROM catalogs AS c\n'
  catalogs_where    = 'WHERE %s\n'
  catalogs_order_by = 'ORDER BY %s\n' % (get_order_clause(order_by), )
  catalogs_limit    = '' if page_info is None else (str(page_info) + '\n')
  
  catalogs_args = tuple()
  
  if catalog_filter.id is not None:
    catalogs_where %= 'id = %s'
    catalogs_args = (catalog_filter.id, )
  elif catalog_filter.name is not None:
    catalog_column_name = _name_columns[(catalog_filter.name_is_case_sensitive, catalog_filter.name_matches_diacritics)][1]
    if catalog_filter.name_has_wildcards:
      catalogs_where %= (catalog_column_name + ' LIKE %s')
    else:
      catalogs_where %= (catalog_column_name + ' = %s')
    catalogs_args = (catalog_filter.get_search_adjusted_name(), )
  else:
    catalogs_where = ''
  
  catalogs = []
  query    = catalogs_select + catalogs_from + catalogs_where + catalogs_order_by + catalogs_limit + ';'
  
  with get_cursor(False) as cursor:
    catalog_ct = cursor.execute(query, catalogs_args)
    for i in range(catalog_ct):
      db_catalog = cursor.fetchone()
      
      base_path = db_catalog['catalog_base_path'] if include_base_paths else None
      catalogs.append(Catalog(db_catalog['catalog_id'], db_catalog['catalog_name'], db_catalog['catalog_lcase_name'], db_catalog['catalog_no_diacritic_name'], db_catalog['catalog_lcase_no_diacritic_name'], base_path))
  
  return catalogs

def get_song(catalog_id:int, id_or_filename:[int, str], include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> Song:
  grievances = []
  
  if not isinstance(catalog_id, int):
    grievances.append('a catalog id must be an int.  (found "%s", a %s instead.)' % (str(catalog_id), get_type_name(catalog_id)))
  
  song_filter = default_filter_info
  filename = None
  if isinstance(id_or_filename, int):
    song_filter.id = id_or_filename
  elif isinstance(id_or_filename, str):
    filename = id_or_filename
  else:
    grievances.append('an id or file name must be an int or a string.  (found "%s", a %s instead.)' % (str(id_or_filename), get_type_name(id_or_filename)))
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  result = _get_songs(catalog_id, filename, song_filter, None, None, None, None, None, None, None, include_artists, include_albums, include_genres)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  message = 'id %s' % (str(id), )
  if id is None:
    message = 'filename "%s"' % (filename, )
  
  raise InvalidCountException('%s songs were found with %s.' % (str(len(result)), message))

def get_songs(catalog_id:int, song:FilterInfo, song_year:int, artist:FilterInfo, album:FilterInfo, album_artist:FilterInfo, genre:FilterInfo,
              order_by:list[OrderByCol], page_info:PageInfo,
              include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> list[Song]:
  return _get_songs(catalog_id, None, song, song_year, artist, album, album_artist, genre, order_by, page_info, include_artists, include_albums, include_genres)

_name_separator_for_queries   = '\\n • '
_name_separator_for_splitting = _name_separator_for_queries.replace('\\n', '\n')
get_songs_order_by_type_error = 'order_by for getting songs must be a list of song columns.'
def _get_songs(catalog_id:int, song_filename:str, song_filter:FilterInfo, song_year:int, artist_filter:FilterInfo, album_filter:FilterInfo, album_artist_filter:FilterInfo, genre_filter:FilterInfo,
               order_by:list[OrderByCol], page_info:PageInfo,
               include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> list[Song]:
  if not isinstance(catalog_id, int):
    raise ValueError('got a catalog id that\'s a(n) %s instead of an int: %s' % (get_type_name(catalog_id), str(catalog_id)))
  
  if song_filter is None:
    song_filter = default_filter_info
  elif not isinstance(song_filter, FilterInfo):
    raise ValueError('invalid song filter info for getting songs.')
  
  if artist_filter is None:
    artist_filter = default_filter_info
  elif not isinstance(artist_filter, FilterInfo):
    raise ValueError('invalid artist filter info for getting songs.')
  
  if album_filter is None:
    album_filter = default_filter_info
  elif not isinstance(album_filter, FilterInfo):
    raise ValueError('invalid album filter info for getting songs.')
  
  if album_artist_filter is None:
    album_artist_filter = default_filter_info
  elif not isinstance(album_artist_filter, FilterInfo):
    raise ValueError('invalid album_artist filter info for getting songs.')
  
  if genre_filter is None:
    genre_filter = default_filter_info
  elif not isinstance(genre_filter, FilterInfo):
    raise ValueError('invalid genre filter info for getting songs.')
  
  if order_by is None:
    order_by = default_get_songs_order_by
  elif isinstance(order_by, (list, tuple)):
    if len(order_by) == 0:
      order_by = default_get_songs_order_by
    else:
      for col in order_by:
        if not isinstance(col.col, GetSongsOrderColumns) or not isinstance(col.direction, OrderDirection):
          raise TypeError(get_songs_order_by_type_error)
  else:
    raise TypeError(get_songs_order_by_type_error)
  
  if page_info is not None and not isinstance(page_info, PageInfo):
    raise TypeError('page info must be a page number and a page size.')
  
  songs_select   = 'SELECT s.id AS song_id,\n' \
                   '  s.title AS song_title,\n' \
                   '  s.lcase_title AS song_lcase_title,\n' \
                   '  s.no_diacritic_title AS song_no_diacritic_title,\n' \
                   '  s.lcase_no_diacritic_title AS song_lcase_no_diacritic_title,\n' \
                   '  s.filename AS song_filename,\n' \
                   '  s.year AS song_year,\n' \
                   '  s.duration AS song_duration,\n' \
                   '  c.id AS catalog_id,\n' \
                   '  c.name AS catalog_name,\n' \
                   '  c.lcase_name AS catalog_lcase_name,\n' \
                   '  c.no_diacritic_name AS catalog_no_diacritic_name,\n' \
                   '  c.lcase_no_diacritic_name AS catalog_lcase_no_diacritic_name,\n' \
                   '  GROUP_CONCAT(CONCAT(ar.name, s_ar.conjunction) ORDER BY s_ar.list_order SEPARATOR "") AS artist_name,\n' + \
                  ('  GROUP_CONCAT(CONCAT(ar.id, "%s", ar.name, "%s", ar.lcase_name, "%s", ar.no_diacritic_name, "%s", ar.lcase_no_diacritic_name, "%s", s_ar.list_order, "%s", s_ar.conjunction) ORDER BY s_ar.list_order SEPARATOR "%s") AS artist_names,\n' % ((_name_separator_for_queries,) * 7)) + \
                   '  al.name AS album_name,\n' \
                   '  al_ar.name AS album_artist_name,\n' + \
                  ('  GROUP_CONCAT(CONCAT(al.id, "%s", al.name, "%s", al.lcase_name, "%s", al.no_diacritic_name, "%s", al.lcase_no_diacritic_name, "%s", al_ar.id, "%s", al_ar.name, "%s", al_ar.lcase_name, "%s", al_ar.no_diacritic_name, "%s", al_ar.lcase_no_diacritic_name, "%s", s_al.track_number) ORDER BY al.name SEPARATOR "%s") AS album_names,\n' % ((_name_separator_for_queries,) * 11)) + \
                   '  g.name as genre_name,\n' + \
                  ('  GROUP_CONCAT(CONCAT(g.id, "%s", g.name, "%s", g.lcase_name, "%s", g.no_diacritic_name, "%s", g.lcase_no_diacritic_name) ORDER BY g.name SEPARATOR "%s") AS genre_names\n' % ((_name_separator_for_queries,) * 5))
  songs_from     = 'FROM songs AS s\n' \
                   '  INNER JOIN catalogs AS c ON c.id = s.catalog_id\n' \
                   '  LEFT JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n' \
                   '    LEFT JOIN artists AS ar ON ar.id = s_ar.artist_id\n' \
                   '  LEFT JOIN songs_albums AS s_al ON s_al.song_id = s.id\n' \
                   '    LEFT JOIN albums AS al ON al.id = s_al.album_id\n' \
                   '      LEFT JOIN artists AS al_ar ON al_ar.id = al.album_artist\n' \
                   '  LEFT JOIN songs_genres AS s_g ON s_g.song_id = s.id\n' \
                   '    LEFT JOIN genres AS g ON g.id = s_g.genre_id\n'
  songs_where    = 'WHERE c.id = %s\n'
  songs_group_by = 'GROUP BY s.id\n'
  songs_having   = 'HAVING 1=1\n'
  songs_order_by = 'ORDER BY %s\n' % (get_order_clause(order_by), )
  songs_limit    = '' if page_info is None else (str(page_info) + '\n')
  
  songs_from_args  = []
  songs_where_args = [catalog_id]
  
  if song_filter.id is not None:
    songs_where += '  AND s.id = %s\n'
    songs_where_args.append(song_filter.id)
  elif song_filename is not None:
    songs_where += '  AND s.filename = %s\n'
    songs_where_args.append(song_filename)
  
  if song_filter.name is not None:
    song_title_column_name = _name_columns[(song_filter.name_is_case_sensitive, song_filter.name_matches_diacritics)][0]
    if song_filter.name_has_wildcards:
      songs_where += '  AND s.' + song_title_column_name + ' LIKE %s\n'
    else:
      songs_where += '  AND s.' + song_title_column_name + ' = %s\n'
    songs_where_args.append(song_filter.get_search_adjusted_name())
  
  if song_year is not None:
    songs_where += '  AND s.year = %s\n'
    songs_where_args.append(song_year)
  
  if artist_filter.id is not None:
    songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                  '    AND s_ar_filter.artist_id = %s\n'
    songs_from_args.append(artist_filter.id)
  elif artist_filter.name is not None:
    artist_name_column_name = _name_columns[(artist_filter.name_is_case_sensitive, artist_filter.name_matches_diacritics)][1]
    if artist_filter.name_has_wildcards:
      songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                    '    INNER JOIN artists AS ar_filter ON ar_filter.id = s_ar_filter.artist_id\n' \
                    '      AND ar_filter.' + artist_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                    '    INNER JOIN artists AS ar_filter ON ar_filter.id = s_ar_filter.artist_id\n' \
                    '      AND ar_filter.' + artist_name_column_name + ' = %s\n'
    songs_from_args.append(artist_filter.get_search_adjusted_name())
  elif artist_filter.filter_on_null: # artist_id is None and artist_name is None.
      songs_from += '  LEFT JOIN songs_artists AS s_a_filter ON s_a_filter.song_id = s.id\n'
      songs_having += '  AND COUNT(s_a_filter.artist_id) = 0\n'
  
  if album_filter.id is not None:
    songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                  '    AND s_al_filter.album_id = %s\n'
    songs_from_args.append(album_filter.id)
  elif album_filter.name is not None:
    album_name_column_name = _name_columns[(album_filter.name_is_case_sensitive, album_filter.name_matches_diacritics)][1]
    if album_filter.name_has_wildcards:
      songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                    '    INNER JOIN albums AS al_filter ON al_filter.id = s_al_filter.album_id\n' \
                    '      AND al_filter.' + album_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                    '    INNER JOIN albums AS al_filter ON al_filter.id = s_al_filter.album_id\n' \
                    '      AND al_filter.' + album_name_column_name + ' = %s\n'
    
    songs_from_args.append(album_filter.get_search_adjusted_name())
    
    if album_artist_filter.id is not None:
      songs_from += '    AND al_filter.album_artist = %s\n'
      songs_from_args.append(album_artist_filter.id)
    elif album_artist_filter.name is not None:
      album_artist_name_column_name = _name_columns[(album_artist_filter.name_is_case_sensitive, album_artist_filter.name_matches_diacritics)][1]
      songs_from += '    INNER JOIN artists AS al_ar_filter ON al_ar_filter.id = al_filter.album_artist\n'
      if album_artist_filter.name_has_wildcards:
        songs_from += '      AND al_ar_filter.' + album_artist_name_column_name + ' = %s\n'
      else:
        songs_from += '      AND al_ar_filter.' + album_artist_name_column_name + ' LIKE %s\n'
      songs_from_args.append(album_artist_filter.get_search_adjusted_name())
    elif album_artist_filter.filter_on_null: # album_artist.id is None and album_artist.name is None
        songs_from += '    AND al_filter.album_artist IS NULL\n'
  else: # album_is is None and album_name is None
    if album_filter.filter_on_null:
      songs_from += '  LEFT JOIN songs_albums AS s_a_filter ON s_a_filter.song_id = s.id\n'
      songs_having += '  AND COUNT(s_a_filter.album_id) = 0\n'
  
  if genre_filter.id is not None:
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' \
                  '    AND s_g_filter.genre_id = %s\n'
    songs_from_args.append(genre_filter.id)
  elif genre_filter.name is not None:
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' \
                  '    INNER JOIN genres AS g_filter ON g_filter.id = s_g_filter.genre_id\n'
    genre_name_column_name = _name_columns[(genre_filter.name_is_case_sensitive, genre_filter.name_matches_diacritics)][1]
    if genre_filter.name_has_wildcards:
      songs_from += '      AND g_filter.' + genre_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '      AND g_filter.' + genre_name_column_name + ' = %s\n'
    songs_from_args.append(genre_filter.get_search_adjusted_name())
  elif genre_filter.filter_on_null: # genre_id is None and genre_name is None
    songs_from += '  LEFT JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n'
    songs_having += '  AND COUNT(s_g_filter.genre_id) = 0\n'
  
  songs_query = songs_select + songs_from + songs_where + songs_group_by + songs_having + songs_order_by + songs_limit + ';'
  
  songs_args = tuple(songs_from_args + songs_where_args)
  
  songs = []
  artists = dict()
  albums = dict()
  with get_cursor(False) as songs_cursor:
    song_count = songs_cursor.execute(songs_query, songs_args)
    for i in range(song_count):
      db_song = songs_cursor.fetchone()
      
      catalog = Catalog(db_song['catalog_id'], db_song['catalog_name'], db_song['catalog_lcase_name'], db_song['catalog_no_diacritic_name'], db_song['catalog_lcase_no_diacritic_name'], None)
      song_filter = Song(db_song['song_id'], db_song['song_title'], db_song['song_lcase_title'], db_song['song_no_diacritic_title'], db_song['song_lcase_no_diacritic_title'], db_song['song_year'], db_song['song_duration'], db_song['song_filename'], None, catalog, genres=[], songs_artists=[], songs_albums=[])
      
      if include_artists and db_song['artist_names'] is not None:
        artist_names = db_song['artist_names'].split(_name_separator_for_splitting)
        for j in range(0, len(artist_names), 7):
          artist_id = int(artist_names[j])
          artist_filter = None
          if artist_id in artists:
            artist_filter = artists[artist_id]
          else:
            artist_filter = Artist(int(artist_names[j]), artist_names[j + 1], artist_names[j + 2], artist_names[j + 3], artist_names[j + 4])
            artists[artist_id] = artist_filter
          song_artist = SongArtist(song_filter, artist_filter, int(artist_names[j + 5]), artist_names[j + 6])
          song_filter.get_songs_artists().append(song_artist)
      
      if include_albums and db_song['album_names'] is not None:
        album_names = db_song['album_names'].split(_name_separator_for_splitting)
        for j in range(0, len(album_names), 11):
          album_id = int(album_names[j])
          album_filter = None
          if album_id in albums:
            album_filter = albums[album_id]
          else:
            album_artist_id = int(album_names[j + 5])
            album_artist_filter = None
            if album_artist_id in artists:
              album_artist_filter = artists[album_artist_id]
            else:
              album_artist_filter = Artist(album_artist_id, album_names[j + 6], album_names[j + 7], album_names[j + 8], album_names[j + 9])
              artists[album_artist_id] = album_artist_filter
            album_filter = Album(album_id, album_names[j + 1], album_names[j + 2], album_names[j + 3], album_names[j + 4], album_artist_filter)
            albums[album_id] = album_filter
          song_album = SongAlbum(song_filter, album_filter, int(album_names[j + 10]))
          song_filter.get_songs_albums().append(song_album)
      
      if include_genres and db_song['genre_names'] is not None:
        genre_names = db_song['genre_names'].split(_name_separator_for_splitting)
        for j in range(0, len(genre_names), 5):
          genre_id = int(genre_names[j])
          genre_filter = None
          if genre_id in genres:
            genre_filter = genres[genre_id]
          else:
            genre_filter = Genre(genre_id, genre_names[j + 1], genre_names[j + 2], genre_names[j + 3], genre_names[j + 4])
            genres[genre_id] = genre_filter
          song_filter.get_genres().append(genre_filter)
      
      songs.append(song_filter)
  
  return songs

def save_song(song):
  logger = get_logger()
  
  if song.get_filename() is None:
    raise InvalidSongDataException('a song must have a filename.')
  
  logger.info('starting to save %s.' % song.get_filename())
  
  admin = True
  with get_cursor(admin) as cursor:
    # for safety
    query = 'DELETE FROM upsert_song_artist_info WHERE 1=1;\n'
    cursor.execute(query)
    
    if len(song.get_songs_artists()) > 0:
      artist_info_params = []
      query_values = ''
      for s_a in song.get_songs_artists():
        artist_info_params += [s_a.get_artist().get_name(), s_a.get_artist().get_lcase_name(), s_a.get_artist().get_no_diacritic_name(), s_a.get_artist().get_lcase_no_diacritic_name(), s_a.get_conjunction(), s_a.get_list_order()]
        query_values += '\n    (%s, %s, %s, %s, %s, %s),'
      
      query = 'INSERT INTO upsert_song_artist_info (artist_name, artist_lcase_name, artist_no_diacritic_name, artist_lcase_no_diacritic_name, conjunction, list_order)\nVALUES%s;' % (query_values[:-1], )
      cursor.execute(query, tuple(artist_info_params))
    
    in_album_name                     = None
    in_album_lcase_name               = None
    in_album_no_diacritics_name       = None
    in_album_lcase_no_diacritics_name = None
    in_album_artist_name                    = None
    in_album_artist_lcase_name              = None
    in_album_artist_no_diacritic_name       = None
    in_album_artist_lcase_no_diacritic_name = None
    in_track_number = None
    in_genre_name                    = None
    in_genre_lcase_name              = None
    in_genre_no_diacritic_name       = None
    in_genre_lcase_no_diacritic_name = None
    
    genre:Genre = None
    for g in song.get_genres():
      genre = g
      break
    
    if genre is not None:
      in_genre_name                    = genre.get_name()
      in_genre_lcase_name              = genre.get_lcase_name()
      in_genre_no_diacritic_name       = genre.get_no_diacritic_name()
      in_genre_lcase_no_diacritic_name = genre.get_lcase_no_diacritic_name()
    
    song_album = song.get_songs_albums()[0] if len(song.get_songs_albums()) > 0 else None
    if song_album is not None:
      in_album_name = song_album.get_album().get_name()
      in_album_lcase_name = song_album.get_album().get_lcase_name()
      in_album_no_diacritics_name = song_album.get_album().get_no_diacritic_name()
      in_album_lcase_no_diacritics_name = song_album.get_album().get_lcase_no_diacritic_name()
      in_track_number = song_album.get_track_number()
  
      album_artist:Artist = song_album.get_album().get_album_artist()
      if album_artist is not None:
        in_album_artist_name                    = album_artist.get_name()
        in_album_artist_lcase_name              = album_artist.get_lcase_name()
        in_album_artist_no_diacritic_name       = album_artist.get_no_diacritic_name()
        in_album_artist_lcase_no_diacritic_name = album_artist.get_lcase_no_diacritic_name()
    
    proc_args = \
    (
      song.get_title(),  # in_song_title
      song.get_lcase_title(),
      song.get_no_diacritic_title(),
      song.get_lcase_no_diacritic_title(),
      song.get_filename(),  # in_filename
      song.get_year(),  # in_year
      song.get_duration(), # in_duration
      song.get_catalog().get_id(),  # in_catalog_id
      in_album_name,
      in_album_lcase_name,
      in_album_no_diacritics_name,
      in_album_lcase_no_diacritics_name,
      in_album_artist_name,
      in_album_artist_lcase_name,
      in_album_artist_no_diacritic_name,
      in_album_artist_lcase_no_diacritic_name,
      in_track_number,
      in_genre_name,
      in_genre_lcase_name,
      in_genre_no_diacritic_name,
      in_genre_lcase_no_diacritic_name,
      song.get_file_last_modified()
    )
    
    logger.info('saving ' + str(song) + ' from "' + song.get_full_filename() + '" to the database...')
    logger.debug('proc args: ' + str(proc_args))
    cursor.callproc('upsert_song', proc_args) # python won't get the result returned by mysql.  \-:
    commit(admin)
    
    cursor.execute('SELECT id FROM songs WHERE filename="%s";' % song.get_filename())
    song_id = cursor.fetchone()['id']
    logger.debug('last insert id was ' + str(song_id))
    song.set_id(song_id)
  
  commit(admin)
  logger.info('done saving %s' % song.get_filename())

def get_artist(artist_identifier:[int, str], include_songs:bool = False, include_albums:IncludeAlbumModes = IncludeAlbumModes.ALBUM_ARTIST_ONLY, include_album_tracks:bool = False, include_genres:bool = False) -> Artist:
  artist_id = None
  artist_name = None
  if isinstance(artist_identifier, int):
    artist_id = artist_identifier
  elif isinstance(artist_identifier, str):
    artist_name = artist_identifier
  else:
    raise TypeError('an identifier for an artist must be an integer or a string.')
  
  artist_filter = FilterInfo(artist_id, artist_name, False, True, True, False)
  genre_filter  = default_filter_info
  artists = get_artists(None, artist_filter, genre_filter, None, None, include_songs, include_albums, include_album_tracks, include_genres)
  
  if len(artists) == 0:
    return None
  
  if len(artists) == 1:
    return artists[0]
  
  raise ValueError('%s artists were found that were identified by "%s".' % (len(artists), artist_identifier))

get_artists_order_by_type_error = '"order by" must be a list of GetArtistsOrderColumns.'
def get_artists(catalog_id:int, artist_filter:FilterInfo, genre_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo, include_songs:bool = False, include_albums:IncludeAlbumModes = IncludeAlbumModes.ALBUM_ARTIST_ONLY, include_album_tracks:bool = False, include_genres:bool = False) -> list[Artist]:
  grievances = []
  
  if catalog_id is not None and not isinstance(catalog_id, int):
    grievances.append('a catalog id must be an integer.')
  
  if not isinstance(artist_filter, FilterInfo):
    grievances.append('an artist filter must be filter info.')
  
  if not isinstance(genre_filter, FilterInfo):
    grievances.append('a genre filter must be filter info.')
  
  if order_by is None:
    order_by = default_get_artists_order_by
  elif isinstance(order_by, (list, tuple)):
    for ob in order_by:
      if not isinstance(ob, OrderByCol) or not isinstance(ob.col, GetArtistsOrderColumns):
        grievances.append(get_artists_order_by_type_error)
        break
  else:
    grievances.append(get_artists_order_by_type_error)
  
  if page_info is not None and not isinstance(page_info, PageInfo):
    grievances.append('page info must be a PageInfo.')
  
  if not isinstance(include_songs, bool):
    grievances.append('the "include songs" flag must be a boolean.')
  
  if not isinstance(include_albums, IncludeAlbumModes):
    grievances.append('the "include albums" flag must be an include albums mode.')
  
  if not isinstance(include_album_tracks, bool):
    grievances.append('the "include album tracks" flag must be a boolean.')
  
  artists_select   = 'SELECT\n' \
                     '  ar.id AS artist_id,\n' \
                     '  ar.name AS artist_name,\n' \
                     '  ar.lcase_name AS artist_lcase_name,\n' \
                     '  ar.no_diacritic_name AS artist_no_diacritic_name,\n' \
                     '  ar.lcase_no_diacritic_name AS artist_lcase_no_diacritic_name\n'
  artists_from     = 'FROM artists AS ar\n' \
                     '  LEFT JOIN songs_artists AS s_ar_cat_filter ON s_ar_cat_filter.artist_id = ar.id\n' \
                     '    LEFT JOIN songs AS s_cat_filter_from_ar ON s_cat_filter_from_ar.song_id = s_ar_cat_filter.song_id\n' \
                     '      AND s_cat_filter_from_ar.catalog_id = %s\n' \
                     '  LEFT JOIN albums AS al_cat_filter ON al_cat_filter.album_artist = ar.id\n' \
                     '    LEFT JOIN songs_albums AS s_al_cat_filter ON s_al_cat_filter.album_id = al.id\n' \
                     '      LEFT JOIN songs AS s_cat_filter_from_al ON s_cat_filter_from_al.id = s_al_cat_filter.song_id\n' \
                     '        AND s_cat_filter_from_al.catalog_id = %s\n'
  artists_where    = 'WHERE %s\n'
  artists_group_by = 'GROUP BY ar.id\n'
  artists_having   = 'HAVING COUNT(s_cat_filter_from_ar) > 0 OR COUNT(s_cat_filter_from_al.id) > 0\n'
  artists_order_by = 'ORDER BY %s\n' % (get_order_clause(order_by), )
  artists_limit    = '' if page_info is None else (str(page_info) + '\n')
  
  artists_from_args  = [catalog_id, catalog_id]
  artists_where_args = []
  
  if artist_filter.id is not None:
    artists_where %= 'ar.id = %s'
    artists_where_args.append(artist_filter.id)
  elif artist_filter.name is not None:
    column_name = _name_columns[(artist_filter.name_is_case_sensitive, artist_filter.name_matches_diacritics)][1]
    if artist_filter.name_has_wildcards:
      artists_where %= ('ar.' + column_name + ' LIKE %s')
    else:
      artists_where %= ('ar.' + column_name + ' = %s')
    artists_where_args.append(artist_filter.get_search_adjusted_name())
  
  if genre_filter.id is not None or genre_filter.name is not None:
    artists_from += '  INNER JOIN songs_artists AS s_ar_genre_filter ON s_ar_genre_filter.artist_id = ar.id\n' \
                    '    INNER JOIN songs_genres AS s_g_genre_filter ON s_g_genre_filter.song_id = s_ar_genre_filter.song_id\n'
    
    if genre_filter.id is not None:
      artists_from += '      AND s_g_genre_filter.genre_id = %s'
      artists_from_args.append(genre_filter.id)
    elif genre_filter.name is not None:
      artists_from += '      INNER JOIN genres AS g_genre_filter ON g_genre_filter.id = s_g_genre_filter.genre_id\n'
      genre_name_column = _name_columns[(genre_filter.name_is_case_sensitive, genre_filter.name_matches_diacritics)][1]
      if genre_filter.name_has_wildcards:
        artists_from += '        AND g_genre_filter.' + genre_name_column + ' LIKE %s\n'
      else:
        artists_from += '        AND g_genre_filter.' + genre_name_column + ' = %s\n'
      artists_from_args.append(genre_filter.get_search_adjusted_name())
  
  artists_query = artists_select + artists_from + artists_where + artists_group_by + artists_having + artists_order_by + artists_limit + ';'
  artists_args  = tuple(artists_from_args + artists_where_args)
  artists       = []
  
  with get_cursor() as cursor:
    artist_ct = cursor.execute(artists_query, artists_args)
    for i in range(artist_ct):
      db_artist = cursor.fetchone()
      artist = Artist(db_artist['artist_id'], db_artist['artist_name'], db_artist['artist_lcase_name'], db_artist['artist_no_diacritic_name'], db_artist['artist_lcase_no_diacritic_name'])
  
      artist_filter_i = FilterInfo(artist.get_id(), None, False, True, True, False)
      if include_songs:
        songs = _get_songs(catalog_id, None, None, None, artist_filter_i, None, None, None, None, None)
        songs_artists = [SongArtist(s, artist, None, None) for s in songs]
        artist.set_songs_artists(songs_artists)
      
      if include_albums:
        raise NotImplementedException('!')
      
      if include_genres:
        genres_query = 'SELECT\n' \
                       '  g.id AS genre_id,\n' \
                       '  g.name AS genre_name,\n' \
                       '  g.lcase_name AS genre_lcase_name,\n' \
                       '  g.no_diacritic_name AS genre_no_diacritic_name,\n' \
                       '  g.lcase_no_diacritic_name AS genre_lcase_no_diacritic_name\n' \
                       'FROM genres AS g\n' \
                       '  INNER JOIN songs_genres AS s_g ON s_g.genre_id = g.id\n' \
                       '    INNER JOIN songs_artists AS s_ar ON s_ar.song_id = s_g.song_id\n' \
                       '      AND s_ar.artist_id = %s\n' \
                       'ORDER BY genre_name;'
        genres_args = (artist.get_id(), )
        artist_genres = []
        with get_cursor() as genre_cursor:
          genre_ct = genre_cursor.execute(genres_query, genres_args)
          for j in range(genre_ct):
            db_genre = genre_cursor.fetchone()
            genre_id = db_genre['genre_id']
            genre    = None
            if genre_id in genres:
              genre = genres[genre_id]
            else:
              genre = Genre(genre_id, db_genre['genre_name'], db_genre['genre_lcase_name'], db_genre['genre_no_diacritic_name'], db_genre['genre_lcase_no_diacritic_name'])
              genres[genre_id] = genre
            artist_genres.append(genre)
        artist.set_genres(artist_genres)
      
      artists.append(artist)
  
  return artists

def get_album(album_identifier:[int, str], include_tracks:bool = False) -> Album:
  id_type    = 'id'
  album_id   = None
  album_name = None
  if isinstance(album_identifier, int):
    album_id = album_identifier
  elif isinstance(album_identifier, str):
    id_type = 'name'
    album_name = album_identifier
  else:
    raise TypeError('an album identifier must be an integer (id) or string (name).')
  
  album_filter = FilterInfo(album_id, album_name, False, True, True, False)
  albums = _get_albums(None, album_filter, None, None, None, include_tracks)
  
  if len(albums) == 0:
    return None
  
  if len(albums) == 1:
    return albums[0]
  
  raise InvalidCountException('found %s albums with the id %s.' % (str(len(albums)), str(album_id)))

get_albums_order_by_type_error = 'order_by must be a list of GetAlbumsOrderByCols.'
def _get_albums(catalog_id:int, album_filter:FilterInfo, album_artist_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo, include_tracks:bool = True):
  grievances = []
  
  if album_filter is None:
    album_filter = default_filter_info
  elif not isinstance(album_filter, FilterInfo):
    grievances.append('an album filter must be filter info.')
  
  if album_artist_filter is None:
    album_artist_filter = default_filter_info
  elif not isinstance(album_artist_filter, FilterInfo):
    grievances.append('an album artist filter must be filter info.')
  
  if order_by is None:
    order_by = default_get_albums_order_by
  elif isinstance(order_by, (list, tuple)):
    if len(order_by) == 0:
      order_by = default_get_albums_order_by
    else:
      for ob in order_by:
        if not isinstance(ob, OrderByCol) or not isinstance(ob.col, GetAlbumsOrderColumns):
          grievances.append(get_albums_order_by_type_error)
          break
  else:
    grievances.append(get_albums_order_by_type_error)
  
  if page_info is not None and not isinstance(page_info, PageInfo):
    grievances.append('page_info must be page info.')
  
  if not isinstance(include_tracks, bool):
    grievances.append('the "include tracks" flag must be a boolean.')
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  albums_select   = 'SELECT\n' \
                    '  al.id AS album_id,\n' \
                    '  al.name AS album_name, al.lcase_name as album_lcase_name, al.no_diacritic_name as album_no_diacritic_name, al.lcase_no_diacritic_name as album_lcase_no_diacritic_name,\n' \
                    '  ar.id AS album_artist_id,\n' \
                    '  ar.name AS album_artist_name, ar.lcase_name AS album_artist_lcase_name, ar.no_diacritic_name AS album_artist_no_diacritic_name, ar.lcase_no_diacritic_name AS album_artist_no_diacritic_name\n'
  albums_from     = 'FROM albums AS al\n' \
                    '  LEFT JOIN artists AS ar ON ar.id = al.album_artist_id\n'
  albums_where    = 'WHERE 1=1\n'
  albums_order_by = 'ORDER BY %s\n' % (get_order_clause(order_by), )
  albums_limit    = '' if page_info is None else (str(page_info) + '\n')
  
  albums_where_args = []
  
  if catalog_id is not None and not isinstance(catalog_id, int):
    grievances.append(invalid_catalog_id_error)
  
  if album_filter.id is not None:
    albums_where += '  AND al.id = %s\n'
    albums_where_args.append(album_filter.id)
  elif album_filter.name is not None:
    name_column = _name_columns[(album_filter.name_is_case_sensitive, album_filter.name_matches_diacritics)][1]
    if album_filter.name_has_wildcards:
      albums_where += '  AND al.' + name_column + ' LIKE %s\n'
    else:
      albums_where += '  AND al.' + name_column + ' = %s\n'
    albums_where_args.append(album_filter.get_search_adjusted_name())
  
  if album_artist_filter.id is not None:
    albums_where += '  AND al.album_artist = %s\n'
    albums_where_args.append(album_artist_filter.id)
  elif album_artist_filter.name is not None:
    name_column = _name_columns[(album_artist_filter.name_is_case_sensitive, album_artist_filter.name_matches_diacritics)][1]
    if album_artist_filter.name_has_wildcards:
      albums_where += '  AND ar.' + name_column + ' LIKE %s\n'
    else:
      albums_where += '  AND ar.' + name_column + ' = %s\n'
    albums_where_args.append(album_artist_filter.name)
  elif album_artist_filter.filter_on_null:
    albums_where += '  AND al.album_artist IS NULL\n'
  
  albums_query = albums_select + albums_from + albums_where + albums_order_by + albums_limit + ';'
  albums_args  = tuple(albums_where_args)
  albums       = []
  with get_cursor(False) as cursor:
    num_rows = cursor.execute(albums_query, albums_args)
    
    for i in range(num_rows):
      db_album = cursor.fetchone()
      
      album_artist = Artist(db_album['album_artist_id'], db_album['album_artist_name'], db_album['album_artist_lcase_name'], db_album['album_artist_no_diacritic_name'], db_album['album_artist_lcase_no_diacritic_name'])
      
      album = Album(db_album['id'], db_album['name'], db_album['album_lcase_name'], db_album['album_no_diacritic_name'], db_album['album_lcase_no_diacritic_name'], album_artist)
      albums.append(album)
      
      if not include_tracks:
        continue
      
      album.set_songs_albums([])
      songs = _get_songs(catalog_id, None, None, None, True, None, None, None, True, album.get_id(), None, True, None, None, True, None, None, True, include_albums=False)
      for song in songs:
        sa_query = 'SELECT track_number FROM songs_albums WHERE song_id=%s AND album_id=%s;' % (song.get_id(), album.get_id())
        cursor.execute(sa_query)
        song_album = SongAlbum(song, album, cursor.fetchone()['track_number'])
        album.get_songs_albums().append(song_album)
      
      album.get_songs_albums().sort(key=lambda s_a: s_a.get_track_number())
  
  return albums

def get_genre(catalog_id:int, genre_identifier:[id, str]) -> Genre:
  id_type    = 'id'
  genre_id   = None
  genre_name = None
  if isinstance(genre_identifier, int):
    genre_id = genre_identifier
  elif isinstance(genre_identifier, str):
    id_type = 'name'
    genre_name = genre_identifier
  else:
    raise TypeError('a genre identifier must be either an int (an id) or a string (a name).')
  
  genre_filter = FilterInfo(genre_id, genre_name, False, True, True, False)
  genres = get_genres(catalog_id, genre_filter, None, None)
  
  if len(genres) == 0:
    return None
  
  if len(genres) == 1:
    return genres[0]
  
  raise ValueError('%s genres were found with the %s "%s".' % (len(genres), id_type, genre_identifier))

get_genres_order_by_error_message = 'order_by must be a list or tuple of OrderByCols with genre columns.'
def get_genres(catalog_id:int, genre_filter:FilterInfo, order_by:list[OrderByCol], page_info:PageInfo) -> list[Genre]:
  grievances = []
  
  if catalog_id is not None and not isinstance(catalog_id, int):
    grievances.append('a catalog id must be an int.')
  
  if genre_filter is None:
    genre_filter = default_filter_info
  elif not isinstance(genre_filter, FilterInfo):
    grievances.append('the genre filter for getting genres must be FilterInfo.')
  
  if order_by is None:
    order_by = default_get_genres_order_by
  elif isinstance(order_by, (list, tuple)):
    if len(order_by) == 0:
      order_by = default_get_genres_order_by
    else:
      for ob in order_by:
        if not isinstance(ob, OrderByCol) or not isinstance(ob.col, GetGenresOrderColumns):
          grievances.append(get_genres_order_by_error_message)
          break
  else:
    grievances.append(get_genres_order_by_error_message)
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  genres_select   = 'SELECT\n' \
                    '  g.id AS genre_id,\n' \
                    '  g.name AS genre_name,\n' \
                    '  g.lcase_name AS genre_lcase_name,\n' \
                    '  g.no_diacritic_name AS genre_no_diacritic_name,\n' \
                    '  g.lcase_no_diacritic_name AS genre_lcase_no_diacritic_name\n'
  genres_from     = 'FROM genres AS g\n' \
                    '  INNER JOIN songs_genres AS s_g ON s_g.genre_id = g.id\n' \
                    '    INNER JOIN songs AS s ON s.id = s_g.song_id\n' \
                    '      AND s.catalog_id = %s\n'
  genres_where    = 'WHERE %s\n'
  genres_group_by = 'GROUP BY g.id\n'
  genres_order_by = 'ORDER BY %s\n' % (get_order_clause(order_by), )
  genres_limit    = '' if page_info is None else str(page_info) + '\n'
  
  genre_args = [catalog_id]
  
  if genre_filter.id is not None:
    genres_where %= 'g.id = %s\n'
    genre_args.append(genre_filter.id)
  elif genre_filter.name is not None:
    genre_name_column_name = _name_columns[(genre_filter.name_is_case_sensitive, genre_filter.name_matches_diacritics)][1]
    if genre_filter.name_has_wildcards:
      genres_where %= 'g.' + genre_name_column_name + ' LIKE %s'
    else:
      genres_where %= 'g.' + genre_name_column_name + ' = %s'
    
    genre_args.append(genre_filter.get_search_adjusted_name())
  else:
    genres_where = ''
  
  genres_query = genres_select + genres_from + genres_where + genres_group_by + genres_order_by + genres_limit + ';'
  genres = []
  with get_cursor() as cursor:
    genre_ct = cursor.execute(genres_query, genre_args)
    for i in range(genre_ct):
      db_genre = cursor.fetchone()
      genres.append\
      (
        Genre
        (
          db_genre['genre_id'],
          db_genre['genre_name'],
          db_genre['genre_lcase_name'],
          db_genre['genre_no_diacritic_name'],
          db_genre['genre_lcase_no_diacritic_name']
        )
      )
  
  return genres