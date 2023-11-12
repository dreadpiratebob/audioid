from api.dao.mysql_utils import commit, get_cursor
from api.exceptions.http_base import NotImplementedException
from api.exceptions.song_data import InvalidCountException, InvalidSongDataException
from api.models.db_models import Catalog, Album, Artist, Genre, Song, SongAlbum, SongArtist
from api.util.functions import get_search_text_from_raw_text, get_type_name
from api.util.logger import get_logger

invalid_catalog_id_error = 'a catalog id must be a nonnegative int.'
invalid_artist_id_error = 'an artist id must be a nonnegative int.'
invalid_album_id_error = 'an album id must be a nonnegative int.'
invalid_album_artist_id_error = 'an album artist id must be a nonnegative int.'

genres = dict()

def get_song(catalog_id:int, id_or_filename:(int, str), include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> Song:
  grievances = []
  
  if not isinstance(catalog_id, int):
    grievances.append('a catalog id must be an int.  (found "%s", a %s instead.)' % (str(catalog_id), get_type_name(catalog_id)))
  
  id = None
  filename = None
  if isinstance(id_or_filename, int):
    id = id_or_filename
  elif isinstance(id_or_filename, str):
    filename = id_or_filename
  else:
    grievances.append('an id or file name must be an int or a string.  (found "%s", a %s instead.)' % (str(id_or_filename), get_type_name(id_or_filename)))
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  result = _get_songs(catalog_id, id, filename, None, True, None, None, None, True, None, None, True, None, None, True, None, None, True, include_artists, include_albums, include_genres)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  message = 'id %s' % (str(id), )
  if id is None:
    message = 'filename "%s"' % (filename, )
  
  raise InvalidCountException('%s songs were found with %s.' % (str(len(result)), message))

def get_songs(catalog_id:int, song_name:str, song_title_has_wildcards:bool, song_title_is_case_sensitive:bool, song_title_matches_diacritics:bool, song_year:int,
              artist_id:int, artist_name:str, artist_name_is_an_exact_match:bool,
              album_id:int, album_name:str, album_name_has_wildcards:bool, album_name_is_case_sensitive:bool, album_name_matches_diacritics:bool, filter_on_null_album:bool,
              album_artist_id:int, album_artist_name:str, album_artist_name_has_wildcards:bool, album_artist_name_is_case_sensitive:bool, album_artist_name_matches_diacritics:bool, filter_on_null_album_artist:bool,
              genre_id:int, genre_name:str, genre_name_is_an_exact_match:bool,
              include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> list[Song]:
  return _get_songs(catalog_id, None, None, song_name, song_title_has_wildcards, song_title_is_case_sensitive, song_title_matches_diacritics, song_year,
                    artist_id, artist_name, artist_name_is_an_exact_match,
                    album_id, album_name, album_name_has_wildcards, album_name_is_case_sensitive, album_name_matches_diacritics, filter_on_null_album,
                    album_artist_id, album_artist_name, album_artist_name_has_wildcards, album_artist_name_is_case_sensitive, album_artist_name_matches_diacritics, filter_on_null_album_artist,
                    genre_id, genre_name, genre_name_is_an_exact_match,
                    include_artists, include_albums, include_genres)

_name_columns = \
{
  (True,  True ): ('title', 'name'),
  (False, True ): ('lcase_title', 'lcase_name'),
  (True,  False): ('no_diacritic_title', 'no_diacritic_name'),
  (False, False): ('lcase_no_diacritic_title', 'lcase_no_diacritic_name')
}
def _get_songs(catalog_id:int, song_id:int, song_filename:str, song_title:str, song_title_has_wildcards:bool, song_title_is_case_sensitive:bool, song_title_matches_diacritics:bool, song_year:int,
               artist_id:int, artist_name:str, artist_name_is_an_exact_match:bool,
               album_id:int, album_name:str, album_name_has_wildcards:bool, album_name_is_case_sensitive:bool, album_name_matches_diacritics:bool, filter_on_null_album:bool,
               album_artist_id:int, album_artist_name:str, album_artist_name_has_wildcards:bool, album_artist_name_is_case_sensitive:bool, album_artist_name_matches_diacritics:bool, filter_on_null_album_artist:bool,
               genre_id:int, genre_name:str, genre_name_is_an_exact_match:bool,
               include_artists:bool = True, include_albums:bool = True, include_genres:bool = True) -> list[Song]:
  if not isinstance(catalog_id, int):
    raise ValueError('got a catalog id that\'s a(n) %s instead of an int: %s' % (get_type_name(catalog_id), str(catalog_id)))
  
  songs_select   = 'SELECT s.id AS song_id,\n' \
                   '  s.title AS song_title,\n' \
                   '  s.lcase_title AS song_lcase_title,\n' \
                   '  s.no_diacritic_title AS song_no_diacritic_title,\n' \
                   '  s.lcase_no_diacritic_title AS song_lcase_no_diacritic_title,\n' \
                   '  s.filename AS song_filename,\n' \
                   '  s.year AS song_year,\n' \
                   '  s.duration AS song_duration,\n' \
                   '  c.id as catalog_id,\n' \
                   '  c.name as catalog_name\n'
  songs_from     = 'FROM songs AS s\n' + \
                   '  INNER JOIN catalogs AS c ON c.id = s.catalog_id\n'
  songs_where    = 'WHERE c.id = %s\n'
  songs_group_by = 'GROUP BY s.id\n'
  songs_having   = 'HAVING 1=1\n'
  
  songs_from_args  = []
  songs_where_args = [catalog_id]
  
  if song_id is not None:
    songs_where += '  AND s.id = %s\n'
    songs_where_args.append(song_id)
  elif song_filename is not None:
    songs_where += '  AND s.filename = %s\n'
    songs_where_args.append(song_filename)
  
  if song_title is not None:
    _title_no_case, _title_no_diacritics, _title_no_case_no_diacritics = (None, None, None)
    if not song_title_is_case_sensitive or not song_title_matches_diacritics:
      _title_no_case, _title_no_diacritics, _title_no_case_no_diacritics = get_search_text_from_raw_text(song_title)
      if song_title_is_case_sensitive and song_title_matches_diacritics:
        pass
      elif not song_title_is_case_sensitive and song_title_matches_diacritics:
        song_title = _title_no_case
      elif song_title_is_case_sensitive and not song_title_matches_diacritics:
        song_title = _title_no_diacritics
      else:
        song_title = _title_no_case_no_diacritics
    
    song_title_column_name = _name_columns[(song_title_is_case_sensitive, song_title_matches_diacritics)][0]
    if song_title_has_wildcards:
      songs_where += '  AND s.' + song_title_column_name + ' LIKE %s\n'
    else:
      songs_where += '  AND s.' + song_title_column_name + ' = %s\n'
    songs_where_args.append(song_title)
  
  if song_year is not None:
    songs_where += '  AND s.year = %s\n'
    songs_where_args.append(song_year)
  
  if artist_id is not None:
    songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                  '    AND s_ar_filter.artist_id = %s\n'
    songs_from_args.append(artist_id)
  elif artist_name is not None:
    if artist_name_is_an_exact_match:
      songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                    '    INNER JOIN artists AS ar_filter ON ar_filter.id = s_ar_filter.artist_id\n' \
                    '      AND ar_filter.name = %s\n'
    else:
      songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' \
                    '    INNER JOIN artists AS ar_filter ON ar_filter.id = s_ar_filter.artist_id\n' \
                    '      AND ar_filter.name LIKE %s\n'
    songs_from_args.append(artist_name)
  
  if album_id is None and album_name is None:
    if filter_on_null_album:
      songs_from += '  LEFT JOIN songs_albums AS s_a_filter ON s_a_filter.song_id = s.id\n'
      songs_having += '  AND COUNT(s_a_filter.album_id) = 0\n'
  elif album_id is not None:
    songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                  '    AND s_al_filter.album_id = %s\n'
    songs_from_args.append(album_id)
  elif album_name is not None:
    _name_no_case, _name_no_diacritics, _name_no_case_no_diacritics = (None, None, None)
    if not album_name_is_case_sensitive or not album_name_matches_diacritics:
      _name_no_case, _name_no_diacritics, _name_no_case_no_diacritics = get_search_text_from_raw_text(album_name)
      if song_title_is_case_sensitive and song_title_matches_diacritics:
        pass
      elif not song_title_is_case_sensitive and song_title_matches_diacritics:
        album_name = _name_no_case
      elif song_title_is_case_sensitive and not song_title_matches_diacritics:
        album_name = _name_no_diacritics
      else:
        album_name = _name_no_case_no_diacritics
    
    album_name_column_name = _name_columns[(album_name_is_case_sensitive, album_name_matches_diacritics)][1]
    if album_name_has_wildcards:
      songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                    '    INNER JOIN albums AS al_filter ON al_filter.id = s_al_filter.album_id\n' \
                    '      AND al_filter.' + album_name_column_name + ' LIKE %s\n'
    else:
      songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' \
                    '    INNER JOIN albums AS al_filter ON al_filter.id = s_al_filter.album_id\n' \
                    '      AND al_filter.' + album_name_column_name + ' = %s\n'
    
    songs_from_args.append(album_name)
    
    album_artist_name_column_name = _name_columns[(album_artist_name_is_case_sensitive, album_artist_name_matches_diacritics)][1]
    if album_artist_id is None and album_artist_name is None:
      if filter_on_null_album_artist:
        songs_from += '    AND al_filter.album_artist IS NULL\n'
    elif album_artist_id is not None:
      songs_from += '    AND al_filter.album_artist = %s\n'
      songs_from_args.append(album_artist_id)
    elif album_artist_name is not None:
      songs_from += '    INNER JOIN artists AS al_ar_filter ON al_ar_filter.id = al_filter.album_artist\n'
      if album_artist_name_has_wildcards:
        songs_from += '      AND al_ar_filter.' + album_artist_name_column_name + ' = %s\n'
      else:
        songs_from += '      AND al_ar_filter.' + album_artist_name_column_name + ' LIKE %s\n'
      songs_from_args.append(album_artist_name)
  
  if genre_id is not None:
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' \
                  '    AND s_g_filter.genre_id = %s\n'
    songs_from_args.append(genre_id)
  elif genre_name is not None:
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' \
                  '    INNER JOIN genres AS g_filter ON g_filter.id = s_g_filter.genre_id\n'
    if genre_name_is_an_exact_match:
      songs_from += '      AND g_filter.name = %s\n'
    else:
      songs_from += '      AND g_filter.name LIKE %s\n'
    songs_from_args.append(genre_name)
  
  songs_query = songs_select + songs_from + songs_where + songs_group_by + songs_having + ';'
  
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
        query = 'SELECT a.id as artist_id, a.name as artist_name, a.lcase_name as artist_lcase_name, a.no_diacritic_name as artist_no_diacritic_name, a.lcase_no_diacritic_name as artist_lcase_no_diacritic_name, ' \
                  's_a.conjunction as conjunction, s_a.list_order as list_order\n' \
                'FROM artists AS a\n' \
                '  INNER JOIN songs_artists AS s_a ON s_a.artist_id = a.id\n' \
                '    AND s_a.song_id = %s\n' % (song.get_id(), ) + \
                'ORDER BY s_a.list_order;'
        
        with get_cursor(False) as artists_cursor:
          artist_count = artists_cursor.execute(query)
          
          for ar in range(artist_count):
            db_artist = artists_cursor.fetchone()
            artist_id = db_artist['artist_id']
            artist = None
            if artist_id in artists:
              artist = artists[artist_id]
            else:
              artist = Artist(artist_id, db_artist['artist_name'], db_artist['artist_lcase_name'], db_artist['artist_no_diacritic_name'], db_artist['artist_lcase_no_diacritic_name'])
              artists[artist_id] = artist
            song_artist = SongArtist(song, artist, db_artist['list_order'], db_artist['conjunction'])
            song.get_songs_artists().append(song_artist)
      
      if include_albums:
        query = 'SELECT a.id AS album_id,\n' \
                '  a.name AS album_name,\n' \
                '  a.lcase_name as album_lcase_name,\n' \
                '  a.no_diacritic_name as album_no_diacritic_name,\n' \
                '  a.lcase_no_diacritic_name as album_lcase_no_diacritic_name,\n' \
                '  s_a.track_number AS track_number,\n' \
                '  ar.id AS album_artist_id,\n' \
                '  ar.name AS album_artist_name,\n' \
                '  ar.lcase_name AS album_artist_lcase_name,\n' \
                '  ar.no_diacritic_name AS album_artist_no_diacritic_name,\n' \
                '  ar.lcase_no_diacritic_name AS album_artist_no_diacritic_name\n' \
                'FROM albums AS a\n' \
                '  INNER JOIN songs_albums AS s_a ON s_a.album_id = a.id\n' \
                '    AND s_a.song_id = %s\n' % (song.get_id(), ) + \
                '  LEFT JOIN artists AS ar ON ar.id = a.album_artist\n' \
                'ORDER BY a.name;'
        
        with get_cursor(False) as albums_cursor:
          album_count = albums_cursor.execute(query)
          
          for al in range(album_count):
            db_album = albums_cursor.fetchone()
            album_id = db_album['album_id']
            album = None
            if album_id in albums:
              album = albums[album_id]
            else:
              album_artist_id = db_album['album_artist_id']
              album_artist = None
              if album_artist_id in artists:
                album_artist = artists[album_artist_id]
              else:
                album_artist = Artist(album_artist_id, db_album['album_artist_name'], db_artist['album_artist_lcase_name'], db_artist['album_artist_no_diacritic_name'], db_artist['album_artist_lcase_no_diacritic_name'])
                artists[album_artist_id] = artist
              album = Album(album_id, db_album['album_name'], db_album['album_lcase_name'], db_album['album_no_diacritic_name'], db_album['album_lcase_no_diacritic_name'], album_artist)
              albums[album_id] = album
            song_album = SongAlbum(song, album, db_album['track_number'])
            song.get_songs_albums().append(song_album)
      
      if include_genres:
        query = 'SELECT g.id AS id, g.name AS name\n' \
                'FROM genres AS g\n' \
                '  INNER JOIN songs_genres AS s_g ON s_g.genre_id = g.id\n' \
                '    AND s_g.song_id = %s\n' % (song.get_id(), ) + \
                'ORDER BY g.name;'
        
        with get_cursor(False) as genres_cursor:
          genre_count = genres_cursor.execute(query)
          
          for g in range(genre_count):
            db_genre = genres_cursor.fetchone()
            genre_id = db_genre['id']
            genre = None
            if genre_id in genres:
              genre = genres[genre_id]
            else:
              genre = Genre(genre_id, db_genre['name'])
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
    artist_joins = ',\n    '.join({str((s_a.get_artist().get_name(), s_a.get_artist().get_lcase_name(), s_a.get_artist().get_no_diacritic_name(), s_a.get_artist().get_lcase_no_diacritic_name(), s_a.get_conjunction(), s_a.get_list_order())) for s_a in song.get_songs_artists()})
    # for safety
    query = 'DELETE FROM upsert_song_artist_info WHERE 1=1;\n'
    cursor.execute(query)
    query = 'INSERT INTO upsert_song_artist_info (artist_name, artist_lcase_name, artist_no_diacritic_name, artist_lcase_no_diacritic_name, conjunction, list_order)\nVALUES\n    %s;' % artist_joins
    cursor.execute(query)
    
    in_genre_name = None
    in_album_name                     = None
    in_album_lcase_name               = None
    in_album_no_diacritics_name       = None
    in_album_lcase_no_diacritics_name = None
    in_album_artist_name                    = None
    in_album_artist_lcase_name              = None
    in_album_artist_no_diacritic_name       = None
    in_album_artist_lcase_no_diacritic_name = None
    in_track_number = None
    
    genre = None
    for g in song.get_genres():
      genre = g
      break
    
    if genre is not None:
      in_genre_name = genre.get_name()
    
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
      in_genre_name,
      in_album_name,
      in_album_lcase_name,
      in_album_no_diacritics_name,
      in_album_lcase_no_diacritics_name,
      in_album_artist_name,
      in_album_artist_lcase_name,
      in_album_artist_no_diacritic_name,
      in_album_artist_lcase_no_diacritic_name,
      in_track_number,
      song.get_file_last_modified(),
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