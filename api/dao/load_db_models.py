from api.dao.mysql_utils import commit, get_cursor
from api.exceptions.song_data import InvalidSongDataException
from api.models.db_models import Album, Artist, Song, SongAlbum, SongArtist, SongGenre
from api.util.logger import get_logger

def get_song(catalog_id:int, id_or_filename:(int, str), include_artists:bool = True, include_albums:bool = True, include_genres:bool = True):
  grievances = []
  
  if not isinstance(catalog_id, int):
    grievances.append('a catalog id must be an int.  (found "%s", a %s instead.)' % (str(catalog_id), str(type(catalog_id))[8:-2]))
  
  id = None
  filename = None
  if isinstance(id_or_filename, int):
    id = id_or_filename
  elif isinstance(id_or_filename, str):
    filename = id_or_filename
  else:
    grievances.append('an id or file name must be an int or a string.  (found "%s" a %s instead.)' % (str(id_or_filename), str(type(id_or_filename))[8:-2]))
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  result = _get_songs(catalog_id, id, filename, None, None, None, None, None, include_artists, include_albums, include_genres)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  message = 'id ' + str(id)
  if id is None:
    message = 'filename "' + filename + '"'
  
  raise ValueError('multiple songs were found with ' + message + '!')

def get_songs(song_name:str, song_year:int, catalog_id:int, artist_id:int, album_id:int, genre_id:int, include_artists:bool = True, include_albums:bool = True, include_genres:bool = True):
  return _get_songs(catalog_id, None, None, song_name, song_year, artist_id, album_id, genre_id, include_artists, include_albums, include_genres)

def _get_songs(catalog_id:int, song_id:int, song_filename:str, song_name:str, song_year:int, artist_id:int, album_id:int, genre_id:int, include_artists:bool = True, include_albums:bool = True, include_genres:bool = True):
  songs_select = 'SELECT s.id, s.name, s.year, s.duration, s.filename, s.last_scanned, c.id as catalog_id, c.name as catalog_name,\n' + \
                 '  GROUP_CONCAT(DISTINCT CONCAT("-\\n  id: ", ar.id, "\n  name: \\"", ar.name, "\\"\\n  list_order: ", s_ar.list_order, "\\n  conjunction: \\"", s_ar.conjunction, "\\"") ORDER BY s_ar.list_order SEPARATOR "\\n") as artists,\n' + \
                 '  GROUP_CONCAT(DISTINCT CONCAT("-\\n  id: ", al.id, "\n  name: \\"", al.name, "\\"\\n  track_number: ", s_al.track_number) ORDER BY al.name, s_al.track_number SEPARATOR "\\n") AS albums'
  songs_from = 'FROM songs AS s\n' + \
               '  INNER JOIN catalogs AS c ON c.id = s.catalog_id\n' + \
               '  LEFT JOIN songs_artists AS s_ar ON s_ar.song_id = s.id\n' + \
               '    LEFT JOIN artists AS ar ON ar.id = s_ar.artist_id\n' + \
               '  LEFT JOIN songs_albums AS s_al ON s_al.song_id = s.id\n' + \
               '    LEFT JOIN albums AS al ON al.id = s_al.album_id\n' + \
               '  LEFT JOIN songs_genres AS s_g ON s_g.song_id = s.id\n' + \
               '    LEFT JOIN genres AS g ON g.id = s_g.genre_id\n'
  songs_where = 'WHERE c.id = (catalog_id)s\n'
  songs_group_by = 'GROUP BY s.id'
  
  songs_args = \
  {
    'catalog_id': catalog_id
  }
  
  if song_id is not None:
    key = 'song_id'
    songs_where += ('  AND s.id = (%s)s\n' % key)
    songs_args[key] = song_id
  
  if song_filename is not None:
    key = 'song_filename'
    songs_where += ('  AND s.filename = (%s)s\n' % key)
    songs_args[key] = song_filename
  
  if song_name is not None:
    key = 'song_name'
    songs_where += ('  AND s.name = (%s)s\n' % key)
    songs_args[key] = song_name
  
  if song_year is not None:
    key = 'song_year'
    songs_where += ('  AND s.year = (%s)s\n' % key)
    songs_args[key] = song_year
  
  if artist_id is not None:
    key = 'artist_id'
    songs_from += '  INNER JOIN songs_artists AS s_ar_filter ON s_ar_filter.song_id = s.id\n' + \
                 ('    AND s_ar_filter.artist_id = (%s)s\n' % key)
    songs_args[key] = artist_id
  
  if album_id is not None:
    key = 'album_id'
    songs_from += '  INNER JOIN songs_albums AS s_al_filter ON s_al_filter.song_id = s.id\n' + \
                 ('    AND s_ar_filter.album_id = (%s)s\n' % key)
    songs_args[key] = album_id
  
  if genre_id is not None:
    key = 'genre_id'
    songs_from += '  INNER JOIN songs_genres AS s_g_filter ON s_g_filter.song_id = s.id\n' + \
                 ('    AND s_g_filter.genre_id = (%s)s\n' % key)
    songs_args[key] = genre_id
  
  songs_query = songs_select + songs_from + songs_where + songs_group_by
  
  print(songs_query)
  
  songs = []
  with get_cursor(True) as cursor:
    row_count = cursor.execute(songs_query, songs_args)
    for i in range(row_count):
      row = cursor.fetchone()
      
  
  return songs

def save_song(song):
  logger = get_logger()
  
  if song.get_filename() is None:
    raise InvalidSongDataException('a song must have a filename.')
  
  logger.info('starting to save %s.' % song.get_filename())
  
  admin = True
  with get_cursor(admin) as cursor:
    in_genre_name = None
    in_album_name = None
    in_album_artist_name = None
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
      in_track_number = song_album.get_track_number()
      
      if song_album.get_album().get_album_artist() is not None:
        in_album_artist_name = song_album.get_album().get_album_artist().get_name()
    
    proc_args = \
    (
      song.get_name(),  # in_song_name
      song.get_filename(),  # in_filename
      song.get_year(),  # in_year
      song.get_duration(), # in_duration
      song.get_catalog().get_id(),  # in_catalog_id
      in_genre_name,
      in_album_name,
      in_album_artist_name,
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
    
    cursor.execute('DELETE FROM songs_artists WHERE song_id = %s' % song.get_id())
    
    for song_artist in song.get_songs_artists():
      proc_args = \
      (
        song_artist.get_artist().get_name(),
        song.get_id(),
        song_artist.get_list_order(),
        song_artist.get_conjunction(),
        False # out_success
      )
      
      logger.info('associating ' + str(song) + ' with ' + str(song_artist.get_artist()) + '...')
      cursor.callproc('link_song_to_artist', proc_args)
  
  commit(admin)
  logger.info('done saving %s' % song.get_filename())


invalid_album_id_error = 'an album id must be a nonnegative int.'


def get_album_by_id(album_id: int, include_tracks: bool = False):
  if not isinstance(album_id, int):
    raise TypeError(invalid_album_id_error)
  
  if album_id < 0:
    raise ValueError(invalid_album_id_error)
  
  query = 'SELECT al.id AS id, al.name AS name,\n' \
          '  ar.id AS album_artist_id, ar.name AS album_artist_name\n' \
          'FROM albums AS al\n' \
          '  LEFT JOIN artists AS ar ON ar.id = al.artist_id\n' \
          'WHERE id = %s' % (str(album_id),)
  
  db_album = None
  with get_cursor(False) as cursor:
    num_rows = cursor.execute(query)
    
    if num_rows == 0:
      return None
    
    db_album = cursor.fetchone
  
  album_artist = Artist(db_album['album_artist_id'], db_album['album_artist_name'])
  
  album = Album(db_album['id'], db_album['name'], album_artist)
  
  if not include_tracks:
    return album
  
  query = 'SELECT s.id AS id, s.name AS name, s.year AS year, s.duration AS duration'
  
  song = Song(db_song['id'], db_song['name'], db_song['year'], db_song['duration'], None, None, catalog)