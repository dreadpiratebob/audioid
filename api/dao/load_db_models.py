from api.dao.mysql_utils import commit, get_cursor
from api.exceptions.http_base import NotImplementedException
from api.exceptions.song_data import InvalidCountException, InvalidSongDataException
from api.models.db_models import Catalog, Album, Artist, Genre, Song, SongAlbum, SongArtist
from api.util.logger import get_logger

genres = dict()

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
  
  raise InvalidCountException('found %s songs were found with %s.' % (str(len(result)), message))

def get_songs(song_name:str, song_year:int, catalog_id:int, artist_id:int, album_id:int, genre_id:int, include_artists:bool = True, include_albums:bool = True, include_genres:bool = True):
  return _get_songs(catalog_id, None, None, song_name, song_year, artist_id, album_id, genre_id, include_artists, include_albums, include_genres)

def _get_songs(catalog_id:int, song_id:int, song_filename:str, song_name:str, song_year:int, artist_id:int, album_id:int, genre_id:int, include_artists:bool = True, include_albums:bool = True, include_genres:bool = True):
  songs_select = 'SELECT s.id AS song_id,\n' \
                 '  s.name AS song_name,\n' \
                 '  s.year AS song_year,\n' \
                 '  s.duration AS song_duration,\n' \
                 '  c.id as catalog_id,\n' \
                 '  c.name as catalog_name\n'
  songs_from = 'FROM songs AS s\n' + \
               '  INNER JOIN catalogs AS c ON c.id = s.catalog_id\n'
  songs_where = 'WHERE c.id = (catalog_id)s\n'
  
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
  
  songs_query = songs_select + songs_from + songs_where
  
  get_logger().debug('get songs query: %s' % (songs_query, ))
  
  songs = []
  artists = dict()
  albums = dict()
  with get_cursor(False) as songs_cursor:
    song_count = songs_cursor.execute(songs_query, songs_args)
    for i in range(song_count):
      db_song = songs_cursor.fetchone()
      
      catalog = Catalog(db_song['catalog_id'], db_song['catalog_name'], None)
      song = Song(db_song['song_id'], db_song['song_name'], db_song['song_year'], db_song['song_duration'], None, None, catalog, genres=[], songs_artists=[], songs_albums=[])
      
      if include_artists:
        query = 'SELECT a.id as id, a.name as name, s_a.conjunction as conjunction, s_a.list_order as list_order\n' \
                'FROM artists AS a' \
                '  INNER JOIN songs_artists AS s_a ON s_a.artist_id = a.id\n' \
                '    AND s_a.song_id = %s;' % (song.get_id(), ) + \
                'ORDER BY s_a.list_order'
        with get_cursor(False) as artists_cursor:
          artist_count = artists_cursor.execute(query)
          for ar in range(artist_count):
            db_artist = artists_cursor.fetchone()
            artist_id = db_artist['id']
            artist = None
            if artist_id in artists:
              artist = artists[artist_id]
            else:
              artist = Artist(artist_id, db_artist['name'])
              artists[artist_id] = artist
            song_artist = SongArtist(song, artist, db_artist['list_order'], db_artist['list_order'])
            song.get_songs_artists().append(song_artist)
      
      if include_albums:
        query = 'SELECT a.id AS id,\n' \
                '  a.name AS name,\n' \
                '  s_a.track_number AS track_number,\n' \
                '  ar.id AS album_artist_id,\n' \
                '  ar.name AS album_artist_name\n' \
                'FROM albums AS a' \
                '  INNER JOIN songs_albums AS s_a ON s_a.album_id = a.id\n' \
                '    AND s_a.song_id = %s;' % (song.get_id(), ) + \
                '  LEFT JOIN artists AS ar ON a.album_artist_id = ar.id\n' \
                'ORDER BY a.name'
        with get_cursor(False) as albums_cursor:
          album_count = albums_cursor.execute(query)
          for al in range(album_count):
            db_album = albums_cursor.fetchone()
            album_id = db_album['id']
            album = None
            if album_id in albums:
              album = albums[album_id]
            else:
              album_artist_id = db_album['album_artist_id']
              album_artist = None
              if album_artist_id in artists:
                album_artist = artists[album_artist_id]
              else:
                album_artist = Artist(album_artist_id, db_album['album_artist_name'])
                artists[album_artist_id] = artist
              album = Album(album_id, db_album['name'], album_artist)
              albums[album_id] = album
            song_album = SongAlbum(song, album, db_album['track_number'])
            song.get_songs_albums().append(song_album)
      
      if include_genres:
        query = 'SELECT g.id AS id, g.name AS name\n' \
                'FROM genres AS g' \
                '  INNER JOIN songs_genres AS s_g ON s_g.genre_id = g.id\n' \
                '    AND s_g.song_id = %s;' % (song.get_id(), ) + \
                'ORDER BY g.name'
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
    artist_joins = ',\n    '.join({str((s_a.get_artist().get_name(), s_a.get_conjunction(), s_a.get_list_order())) for s_a in song.get_songs_artists()})
    query = 'INSERT INTO upsert_song_artist_info (artist_name, conjunction, list_order)\nVALUES\n    %s;' % artist_joins
    logger.debug('running query:\n%s' % (query, ))
    result = cursor.execute(query)
    logger.debug('got result "%s"' % (result, ))
    
    query = 'SELECT COUNT(*) AS ct FROM upsert_song_artist_info;'
    cursor.execute(query)
    result = cursor.fetchone()
    if result is None:
      logger.debug('got None for a count.')
    else:
      logger.debug('inserted %s rows.' % (result['ct']))
    
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
  
  commit(admin)
  logger.info('done saving %s' % song.get_filename())

invalid_album_id_error = 'an album id must be a nonnegative int.'
def get_album_by_id(album_id:int, include_tracks:bool = False):
  result = _get_albums(None, album_id, None, include_tracks)
  
  if len(result) == 0:
    return None
  
  if len(result) == 1:
    return result[0]
  
  raise InvalidCountException('found %s albums with the id %s.' % (str(len(result)), str(album_id)))

def get_album_by_name(album_name:str, include_tracks:bool = False):
  raise NotImplementedException('')

def _get_albums(catalog_id:int, album_id:int, album_name:str, song_id:int, include_tracks:bool = True):
  if not isinstance(album_id, int):
    raise TypeError(invalid_album_id_error)
  
  if album_id < 0:
    raise ValueError(invalid_album_id_error)
  
  query = 'SELECT al.id AS id, al.name AS name,\n' \
          '  ar.id AS album_artist_id, ar.name AS album_artist_name\n' \
          'FROM albums AS al\n' \
          '  LEFT JOIN artists AS ar ON ar.id = al.artist_id\n' \
          'WHERE id = %s' % (str(album_id),)
  
  albums = []
  with get_cursor(False) as cursor:
    num_rows = cursor.execute(query)
    
    for i in range(num_rows):
      db_album = cursor.fetchone()
      
      album_artist = Artist(db_album['album_artist_id'], db_album['album_artist_name'])
      
      album = Album(db_album['id'], db_album['name'], album_artist)
      albums.append(album)
  
  if not include_tracks:
    return albums
  
  songs = _get_songs()
  
  raise NotImplementedException('getting an album\'s tracks isn\'t done yet.')

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