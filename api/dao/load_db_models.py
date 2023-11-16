from api.dao.mysql_utils import commit, get_cursor
from api.exceptions.http_base import NotImplementedException
from api.exceptions.song_data import InvalidCountException, InvalidSongDataException
from api.models.db_models import Catalog, Album, Artist, Genre, Song, SongAlbum, SongArtist
from api.util.audioid.songs import GetSongsOrderColumns, default_get_songs_order_by
from api.util.functions import get_search_text_from_raw_text, get_type_name
from api.util.logger import get_logger
from api.util.response_list_modifiers import \
  FilterInfo, default_filter_info, \
  OrderByCol, \
  OrderDirection, get_order_clause

invalid_catalog_id_error = 'a catalog id must be a nonnegative int.'
invalid_artist_id_error = 'an artist id must be a nonnegative int.'
invalid_album_id_error = 'an album id must be a nonnegative int.'
invalid_album_artist_id_error = 'an album artist id must be a nonnegative int.'

genres = dict()

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
  
  result = _get_songs(catalog_id, filename, song_filter, None, None, None, None, None, None, include_artists, include_albums, include_genres)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  message = 'id %s' % (str(id), )
  if id is None:
    message = 'filename "%s"' % (filename, )
  
  raise InvalidCountException('%s songs were found with %s.' % (str(len(result)), message))

def get_songs(catalog_id:int, song:FilterInfo, song_year:int, artist:FilterInfo, album:FilterInfo, album_artist:FilterInfo, genre:FilterInfo,
              order_by:list[OrderByCol],
              include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> list[Song]:
  return _get_songs(catalog_id, None, song, song_year, artist, album, album_artist, genre, order_by, include_artists, include_albums, include_genres)

_name_separator_for_queries   = '\\n • '
_name_separator_for_splitting = _name_separator_for_queries.replace('\\n', '\n')
_name_columns = \
{
  (True,  True ): ('title', 'name'),
  (False, True ): ('lcase_title', 'lcase_name'),
  (True,  False): ('no_diacritic_title', 'no_diacritic_name'),
  (False, False): ('lcase_no_diacritic_title', 'lcase_no_diacritic_name')
}
get_songs_order_by_type_error = 'order_by for getting songs must be a list of song columns.'
def _get_songs(catalog_id:int, song_filename:str, song:FilterInfo, song_year:int, artist:FilterInfo, album:FilterInfo, album_artist:FilterInfo, genre:FilterInfo,
               order_by:list[OrderByCol],
               include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> list[Song]:
  if not isinstance(catalog_id, int):
    raise ValueError('got a catalog id that\'s a(n) %s instead of an int: %s' % (get_type_name(catalog_id), str(catalog_id)))
  
  if song is None:
    song = default_filter_info
  
  if artist is None:
    artist = default_filter_info
  
  if album is None:
    album = default_filter_info
  
  if album_artist is None:
    album_artist = default_filter_info
  
  if genre is None:
    genre = default_filter_info
  
  if order_by is None:
    order_by = default_get_songs_order_by
  elif not isinstance(order_by, list):
    raise TypeError(get_songs_order_by_type_error)
  else:
    for col in order_by:
      if not isinstance(col.col, GetSongsOrderColumns) or not isinstance(col.direction, OrderDirection):
        raise TypeError(get_songs_order_by_type_error)
  
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
                   '  GROUP_CONCAT(CONCAT(ar.name, s_ar.conjunction) ORDER BY s_ar.list_order SEPARATOR "") AS artist_name,\n' + \
                   ('  GROUP_CONCAT(CONCAT(ar.id, "%s", ar.name, "%s", ar.lcase_name, "%s", ar.no_diacritic_name, "%s", ar.lcase_no_diacritic_name, "%s", s_ar.list_order, "%s", s_ar.conjunction) ORDER BY s_ar.list_order SEPARATOR "%s") AS artist_names,\n' % ((_name_separator_for_queries,) * 7)) + \
                    '  al.name AS album_name,\n' + \
                   ('  GROUP_CONCAT(CONCAT(al.id, "%s", al.name, "%s", al.lcase_name, "%s", al.no_diacritic_name, "%s", al.lcase_no_diacritic_name, "%s", al_ar.id, "%s", al_ar.name, "%s", al_ar.lcase_name, "%s", al_ar.no_diacritic_name, "%s", al_ar.lcase_no_diacritic_name, "%s", s_al.track_number) ORDER BY al.name SEPARATOR "%s") AS album_names,\n' % ((_name_separator_for_queries,) * 11)) + \
                    '  g.name as genre_name,\n' + \
                   ('  GROUP_CONCAT(CONCAT(g.id, "%s", g.name, "%s", g.lcase_name, "%s", g.no_diacritic_name, "%s", g.lcase_no_diacritic_name) ORDER BY g.name SEPARATOR "%s") AS genre_names\n' % ((_name_separator_for_queries,) * 5))
  songs_from     = 'FROM songs AS s\n' \
                   '  INNER JOIN catalogs AS c ON c.id = s.catalog_id\n' \
                   '  LEFT JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n' \
                   '    LEFT JOIN artists AS ar ON ar.id = s_ar.artist_id\n' \
                   '  LEFT JOIN songs_albums AS s_al ON s_al.song_id = s.id\n' \
                   '    LEFT JOIN albums AS al ON al.id = s_al.album_id\n' \
                   '      LEFT JOIN artists AS al_ar ON al_ar.id = al.album_artist' \
                   '  LEFT JOIN songs_genres AS s_g ON s_g.song_id = s.id\n' \
                   '    LEFT JOIN genres AS g ON g.id = s_g.genre_id\n'
  songs_where    = 'WHERE c.id = %s\n'
  songs_group_by = 'GROUP BY s.id\n'
  songs_having   = 'HAVING 1=1\n'
  songs_order_by = 'ORDER BY %s\n' % (get_order_clause(order_by), )
  
  songs_from_args  = []
  songs_where_args = [catalog_id]
  
  if song.id is not None:
    songs_where += '  AND s.id = %s\n'
    songs_where_args.append(song.id)
  elif song_filename is not None:
    songs_where += '  AND s.filename = %s\n'
    songs_where_args.append(song_filename)
  
  if song.name is not None:
    _title_no_case, _title_no_diacritics, _title_no_case_no_diacritics = (None, None, None)
    if not song.name_is_case_sensitive or not song.name_matches_diacritics:
      _title_no_case, _title_no_diacritics, _title_no_case_no_diacritics = get_search_text_from_raw_text(song.name)
      if not song.name_is_case_sensitive and song.name_matches_diacritics:
        song.name = _title_no_case
      elif song.name_is_case_sensitive and not song.name_matches_diacritics:
        song.name = _title_no_diacritics
      else:
        song.name = _title_no_case_no_diacritics
    
    song_title_column_name = _name_columns[(song.name_is_case_sensitive, song.name_matches_diacritics)][0]
    if song.name_has_wildcards:
      songs_where += '  AND s.' + song_title_column_name + ' LIKE %s\n'
    else:
      songs_where += '  AND s.' + song_title_column_name + ' = %s\n'
    songs_where_args.append(song.name)
  
  if song_year is not None:
    songs_where += '  AND s.year = %s\n'
    songs_where_args.append(song_year)
  
  if artist.id is not None:
    songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                  '    AND s_ar_filter.artist_id = %s\n'
    songs_from_args.append(artist.id)
  elif artist.name is not None:
    if not artist.name_is_case_sensitive or not artist.name_matches_diacritics:
      _name_no_case, _name_no_diacritics, _name_no_case_no_diacritics = get_search_text_from_raw_text(artist.name)
      if not artist.name_is_case_sensitive and artist.name_matches_diacritics:
        artist.name = _name_no_case
      elif artist.name_is_case_sensitive and not artist.name_matches_diacritics:
        artist.name = _name_no_diacritics
      else:
        artist.name = _name_no_case_no_diacritics
    
    artist_name_column_name = _name_columns[(artist.name_is_case_sensitive, artist.name_matches_diacritics)][1]
    if artist.name_has_wildcards:
      songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                    '    INNER JOIN artists AS ar_filter ON ar_filter.id = s_ar_filter.artist_id\n' \
                    '      AND ar_filter.' + artist_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                    '    INNER JOIN artists AS ar_filter ON ar_filter.id = s_ar_filter.artist_id\n' \
                    '      AND ar_filter.' + artist_name_column_name + ' = %s\n'
    songs_from_args.append(artist.name)
  elif artist.filter_on_null: # artist_id is None and artist_name is None.
      songs_from += '  LEFT JOIN songs_artists AS s_a_filter ON s_a_filter.song_id = s.id\n'
      songs_having += '  AND COUNT(s_a_filter.artist_id) = 0\n'
  
  if album.id is not None:
    songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                  '    AND s_al_filter.album_id = %s\n'
    songs_from_args.append(album.id)
  elif album.name is not None:
    if not album.name_is_case_sensitive or not album.name_matches_diacritics:
      _name_no_case, _name_no_diacritics, _name_no_case_no_diacritics = get_search_text_from_raw_text(album.name)
      if not album.name_is_case_sensitive and album.name_matches_diacritics:
        album = _name_no_case
      elif album.name_is_case_sensitive and not album.name_matches_diacritics:
        album = _name_no_diacritics
      else:
        album = _name_no_case_no_diacritics
    
    album_name_column_name = _name_columns[(album.name_is_case_sensitive, album.name_matches_diacritics)][1]
    if album.name_has_wildcards:
      songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                    '    INNER JOIN albums AS al_filter ON al_filter.id = s_al_filter.album_id\n' \
                    '      AND al_filter.' + album_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                    '    INNER JOIN albums AS al_filter ON al_filter.id = s_al_filter.album_id\n' \
                    '      AND al_filter.' + album_name_column_name + ' = %s\n'
    
    songs_from_args.append(album.name)
    
    if album_artist.id is not None:
      songs_from += '    AND al_filter.album_artist = %s\n'
      songs_from_args.append(album_artist.id)
    elif album_artist.name is not None:
      if not album_artist.name_is_case_sensitive or not album_artist.name_matches_diacritics:
        _name_no_case, _name_no_diacritics, _name_no_case_no_diacritics = get_search_text_from_raw_text(album_artist.name)
        if not album_artist.name_is_case_sensitive and album_artist.name_matches_diacritics:
          album_artist.name = _name_no_case
        elif album_artist.name_is_case_sensitive and not album_artist.name_matches_diacritics:
          album_artist.name = _name_no_diacritics
        else:
          album_artist.name = _name_no_case_no_diacritics
      
      album_artist_name_column_name = _name_columns[(album_artist.name_is_case_sensitive, album_artist.name_matches_diacritics)][1]
      songs_from += '    INNER JOIN artists AS al_ar_filter ON al_ar_filter.id = al_filter.album_artist\n'
      if album_artist.name_has_wildcards:
        songs_from += '      AND al_ar_filter.' + album_artist_name_column_name + ' = %s\n'
      else:
        songs_from += '      AND al_ar_filter.' + album_artist_name_column_name + ' LIKE %s\n'
      songs_from_args.append(album_artist.name)
    elif album_artist.filter_on_null: # album_artist.id is None and album_artist.name is None
        songs_from += '    AND al_filter.album_artist IS NULL\n'
  else: # album_is is None and album_name is None
    if album.filter_on_null:
      songs_from += '  LEFT JOIN songs_albums AS s_a_filter ON s_a_filter.song_id = s.id\n'
      songs_having += '  AND COUNT(s_a_filter.album_id) = 0\n'
  
  if genre.id is not None:
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' \
                  '    AND s_g_filter.genre_id = %s\n'
    songs_from_args.append(genre.id)
  elif genre.name is not None:
    if not genre.name_is_case_sensitive or not genre.name_matches_diacritics:
      _name_no_case, _name_no_diacritics, _name_no_case_no_diacritics = get_search_text_from_raw_text(genre.name)
      if not genre.name_is_case_sensitive and genre.name_matches_diacritics:
        genre.name = _name_no_case
      elif genre.name_is_case_sensitive and not genre.name_matches_diacritics:
        genre.name = _name_no_diacritics
      else:
        genre.name = _name_no_case_no_diacritics
    
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' \
                  '    INNER JOIN genres AS g_filter ON g_filter.id = s_g_filter.genre_id\n'
    genre_name_column_name = _name_columns[(genre.name_is_case_sensitive, genre.name_matches_diacritics)][1]
    if genre.name_has_wildcards:
      songs_from += '      AND g_filter.' + genre_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '      AND g_filter.' + genre_name_column_name + ' = %s\n'
    songs_from_args.append(genre.name)
  elif genre.filter_on_null: # genre_id is None and genre_name is None
    songs_from += '  LEFT JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n'
    songs_having += '  AND COUNT(s_g_filter.genre_id) = 0\n'
  
  songs_query = songs_select + songs_from + songs_where + songs_group_by + songs_having + songs_order_by + ';'
  
  songs_args = tuple(songs_from_args + songs_where_args)
  
  get_logger().debug('\nsongs_query:\n%s\n\nsongs_args:\n%s' % (songs_query, songs_args))
  
  songs = []
  artists = dict()
  albums = dict()
  with get_cursor(False) as songs_cursor:
    song_count = songs_cursor.execute(songs_query, songs_args)
    for i in range(song_count):
      db_song = songs_cursor.fetchone()
      
      catalog = Catalog(db_song['catalog_id'], db_song['catalog_name'], None)
      song = Song(db_song['song_id'], db_song['song_title'], db_song['song_lcase_title'], db_song['song_no_diacritic_title'], db_song['song_lcase_no_diacritic_title'], db_song['song_year'], db_song['song_duration'], db_song['song_filename'], None, catalog, genres=[], songs_artists=[], songs_albums=[])
      
      if include_artists:
        artist_names = db_song['artist_names'].split(_name_separator_for_splitting)
        for j in range(0, len(artist_names), 7):
          artist_id = int(artist_names[j])
          artist = None
          if artist_id in artists:
            artist = artists[artist_id]
          else:
            artist = Artist(int(artist_names[j]), artist_names[j + 1], artist_names[j + 2], artist_names[j + 3], artist_names[j + 4])
            artists[artist_id] = artist
          song_artist = SongArtist(song, artist, int(artist_names[j + 5]), artist_names[j + 6])
          song.get_songs_artists().append(song_artist)
      
      if include_albums:
        album_names = db_song['album_names'].split(_name_separator_for_splitting)
        for j in range(0, len(album_names), 11):
          album_id = int(album_names[j])
          album = None
          if album_id in albums:
            album = albums[album_id]
          else:
            album_artist_id = int(album_names[j + 5])
            album_artist = None
            if album_artist_id in artists:
              album_artist = artists[album_artist_id]
            else:
              album_artist = Artist(album_artist_id, album_names[j + 6], album_names[j + 7], album_names[j + 8], album_names[j + 9])
              artists[album_artist_id] = album_artist
            album = Album(album_id, album_names[j + 1], album_names[j + 2], album_names[j + 3], album_names[j + 4], album_artist)
            albums[album_id] = album
          song_album = SongAlbum(song, album, int(album_names[j + 10]))
          song.get_songs_albums().append(song_album)
      
      if include_genres:
        genre_names = db_song['genre_names'].split(_name_separator_for_splitting)
        for j in range(0, len(genre_names), 5):
          genre_id = int(genre_names[j])
          genre = None
          if genre_id in genres:
            genre = genres[genre_id]
          else:
            genre = Genre(genre_id, genre_names[j + 1], genre_names[j + 2], genre_names[j + 3], genre_names[j + 4])
            genres[genre_id] = genre
          song.get_genres().append(genre)
      
      songs.append(song)
  
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
      print('query:\n%s\n\nparams:\n%s' % (query, tuple(artist_info_params)))
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

def get_album_by_id(album_id:int, include_tracks:bool = False):
  result = _get_albums(None, album_id, None, include_tracks)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  raise InvalidCountException('found %s albums with the id %s.' % (str(len(result)), str(album_id)))

def get_album_by_name(catalog_id:int, album_name:str, album_artist:[int, str] = None, include_tracks:bool = False):
  album_artist_id = None
  album_artist_name = None
  
  if album_artist is not None:
    if isinstance(album_artist, int):
      album_artist_id = album_artist
    elif isinstance(album_artist, str):
      album_artist_name = album_artist
    else:
      raise TypeError('an album artist must be None, a string (an artist name) or an int (an artist id).')
  
  return _get_albums(catalog_id, None, album_name, album_artist_id, album_artist_name, include_tracks)

def _get_albums(catalog_id:int, album_id:int, album_name:str, album_artist_id:int, album_artist_name:str, include_tracks:bool = True, album_name_has_wildcards:bool = False, artist_name_has_wildcards:bool = False):
  query_select = 'SELECT al.id AS album_id, al.name AS album_name, al.lcase_name as album_lcase_name, al.no_diacritic_name as album_no_diacritic_name, al.lcase_no_diacritic_name as album_lcase_no_diacritic_name,\n' \
                 '  ar.id AS album_artist_id, ar.name AS album_artist_name, ar.lcase_name AS album_artist_lcase_name, ar.no_diacritic_name AS album_artist_no_diacritic_name, ar.lcase_no_diacritic_name AS album_artist_no_diacritic_name\n'
  query_from   = 'FROM albums AS al\n' \
                 '  LEFT JOIN artists AS ar ON ar.id = al.album_artist_id\n'
  query_where  = 'WHERE 1=1'
  
  params = []
  grievances = []
  
  if catalog_id is not None and not isinstance(catalog_id, int):
    grievances.append(invalid_catalog_id_error)
  
  if album_id is not None:
    if isinstance(album_id, int):
      query_where += '\n  AND al.id = %s' % (album_id, )
    else:
      grievances.append(invalid_album_id_error)
  
  if album_name is not None:
    if isinstance(album_name, str):
      if isinstance(album_name_has_wildcards, bool):
        if album_name_has_wildcards:
          query_where += '\n  AND al.name LIKE %s'
        else:
          query_where += '\n  AND al.name = %s'
        params.append(album_name)
      else:
        grievances.append('the "album name has wildcards" flag must be a bool.')
    else:
      grievances.append('an album name must be a string.')
  
  if album_artist_id is not None:
    if isinstance(album_artist_id, int):
      query_where += '\n  AND al.album_artist_id = %s' % (album_artist_id, )
    else:
      grievances.append(invalid_album_artist_id_error)
  
  if album_artist_name is not None:
    if isinstance(album_artist_name, str):
      if isinstance(artist_name_has_wildcards, bool):
        if artist_name_has_wildcards:
          query_where += '\n  AND ar.name LIKE %s'
        else:
          query_where += '\n  AND ar.name = %s'
        params.append(album_artist_name)
      else:
        grievances.append('the "artist name has wildcards" flag must be a bool.')
    else:
      grievances.append('an album artist name must be a string.')
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  if catalog_id < 0:
    grievances.append(invalid_catalog_id_error)
  
  if album_id < 0:
    grievances.append(invalid_album_id_error)
  
  if album_artist_id < 0:
    grievances.append(invalid_album_artist_id_error)
  
  if len(grievances) > 0:
    raise ValueError('\n'.join(grievances))
  
  query = query_select + query_from + query_where
  params = {param for param in params}
  albums = []
  with get_cursor(False) as cursor:
    num_rows = cursor.execute(query, params)
    
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

def get_artist_by_id(artist_id:str, include_songs:bool = False, include_albums:bool = False):
  raise NotImplementedException('')

def get_artist_by_name(artist_name:str, include_songs:bool = False, include_albums:bool = False):
  raise NotImplementedException('')

def get_artists_by_song_id(song_id:str):
  raise NotImplementedException('')

def get_genre_by_id(genre_id:str):
  raise NotImplementedException('')

def get_genre_by_name(genre_name:str):
  raise NotImplementedException('')

def get_genres_by_song_id(song_id:str):
  raise NotImplementedException('')