import sys
sys.path.insert(1, '../')

from time import time

from dao.mysql_utils import commit
from dao.mysql_utils import get_cursor
from exceptions import InvalidSongDataException
from util.logger import get_logger

def save_song(song):
  logger = get_logger()

  if song.filename is None:
    raise InvalidSongDataException('a song must have a filename.')

  logger.info('starting to save %s.' % song.filename)

  def insert_song(song, cursor):
    def get_arg(value, converter):
      if value is None:
        return None

      return converter(value)

    query = 'INSERT INTO songs (name, year, filename, catalog_id, last_scanned) VALUES(%(title)s, %(year)s, %(filename)s, %(catalog_id)s, %(last_scanned)s)'
    args = {'title': get_arg(song.title, str), 'year': get_arg(song.year, int), 'filename': get_arg(song.filename, str), 'catalog_id': get_arg(song.catalog.id, int), 'last_scanned': int(time())}
    logger.debug('executing query: %s' % query)
    logger.debug('args: %s' % str(args))
    cursor.execute(query, args)
    song.id = cursor.lastrowid
  
  def update_song(song, cursor):
    if song.id is None:
      raise InvalidSongDataException('can\'t update a song without a song id.')
    
    query = 'UPDATE songs SET name = %s, year = %x, last_scanned = %x WHERE id = %x'
    cursor.execute(query, (song.title, song.year, int(time()), song.id))
  
  def add_artist_joins(song, cursor):
    if song.id is None:
      raise InvalidSongDataException('can\'t add artists to a song without a song id.')

    song.id = int(song.id)

    query = 'DELETE FROM songs_artists WHERE song_id = %s'
    cursor.execute(query, (song.id, ))
    
    if song.artists is None:
      return
    
    for artist_join in song.artists:
      cursor.execute('SELECT id FROM artists WHERE name=%s', (artist_join.artist.name))
      if cursor.rowcount == 0:
        query = 'INSERT INTO artists (name) VALUES (%s)'
        cursor.execute(query, (artist_join.artist.name, ))
        artist_join.artist.id = cursor.lastrowid
      else:
        sql_artist_data = cursor.fetchone()
        artist_join.artist.id = sql_artist_data['id']
        if cursor.rowcount > 1:
          logger.warn('found multiple artists with the name "%s"; using the one with the id %s.' % (artist_join.artist.name, artist_join.artist.id))
      
      if song.albums is not None:
        for song_album in song.albums:
          album = song_album.album
          if album.album_artist is not None and \
             album.album_artist.id is None and \
             artist_join.artist.name == album.album_artist.name:
            album.album_artist.id = artist_join.artist.id

      if artist_join.conjunction is None:
        artist_join.conjunction = ''

      query = 'INSERT INTO songs_artists (song_id, artist_id, list_order, conjunction) VALUES(%s, %s, %s, %s)'
      cursor.execute(query, (song.id, artist_join.artist.id, artist_join.list_order, artist_join.conjunction))
  
  def add_albums(song, cursor):
    if song.albums is None:
      return
    
    query = 'DELETE FROM songs_albums WHERE song_id = %s'
    cursor.execute(query, (int(song.id), ))

    master_insert_query = 'INSERT INTO songs_albums (song_id, album_id, track_number) VALUES '
    for album_join in song.albums:
      album = album_join.album
      if album.name is None:
        artist_info = ''
        if album.album_artist is not None and album.album_artist.name is not None:
          artist_info = 'by %s ' % album.album_artist.name
        logger.error('found an album %swith a null name. skipping it.' % artist_info)
        continue
      
      if album.album_artist is None:
        query = 'SELECT id FROM albums WHERE name = %s AND album_artist IS NULL;'
        cursor.execute(query, (album.name, ))
      else:
        if album.album_artist.id is None:
          query = 'SELECT id FROM artists WHERE name = %s;'
          cursor.execute(query, (album.album_artist.name,))
          if cursor.rowcount == 0:
            query = 'INSERT INTO artists (name) VALUES (%s);'
            logger.debug('exeucting album query: "%s"' % (query % album.album_artist.name))
            cursor.execute(query, (str(album.album_artist.name),))
            album.album_artist.id = cursor.lastrowid
          else:
            sql_artist_data = cursor.fetchone()
            album.album_artist.id = sql_artist_data['id']
            if cursor.rowcount > 1:
              logger.warn('found multiple artists with the name "%s"; using the one with the id %s.' %
                          (album.album_artist.name, int(album.album_artist.id)))

        query = 'SELECT id FROM albums WHERE name = %s AND album_artist = %s;'
        cursor.execute(query, (album.name, int(album.album_artist.id)))
      
      if cursor.rowcount == 0:
        album_artist_id = None
        if album.album_artist is not None:
          album_artist_id = int(album.album_artist.id)

        query = 'INSERT INTO albums (name, album_artist) VALUES (%s, %s)'
        cursor.execute(query, (album.name, album_artist_id))
        album.id = cursor.lastrowid
      else:
        sql_album_data = cursor.fetchone()
        album.id = sql_album_data['id']
        
        if cursor.rowcount > 1:
          logger.warn('found %x albums with the name "%s" by %s.' % (cursor.rowcount, album.name, 'None' if album.album_artist is None or album.album_artist.name is None else album.album_artist.name))

      master_insert_query = '%s(%s, %s, %s), ' % (master_insert_query, int(song.id), int(album.id), 'NULL' if album_join.track is None else int(album_join.track))

    master_insert_query = '%s;' % master_insert_query[0:len(master_insert_query) - 2]
    cursor.execute(master_insert_query)
  
  def add_genres(song, cursor):
    if song.id is None:
      raise InvalidSongDataException('found a song without an id.')
    
    query = 'DELETE FROM songs_genres WHERE song_id = %s;'
    cursor.execute(query, (int(song.id),))
    
    if song.genres is None:
      return
    
    for genre_join in song.genres:
      genre = genre_join.genre
      if genre is None or genre.name is None:
        continue
      
      query = 'SELECT id FROM genres WHERE name = %s;'
      cursor.execute(query, (genre.name,))
      
      if cursor.rowcount == 0:
        query = 'INSERT INTO genres (name) VALUES (%s);'
        cursor.execute(query, (genre.name,))
        genre.id = cursor.lastrowid
      else:
        sql_genre_data = cursor.fetchone()
        genre.id = sql_genre_data['id']
        
        if cursor.rowcount > 1:
          logger.warn('found %x genres with the name "%s".' % (cursor.rowcount, genre.name))
      
      query = 'INSERT INTO songs_genres (song_id, genre_id) VALUES (%s, %s);'
      cursor.execute(query, (int(song.id), int(genre.id)))
  
  admin = True
  with get_cursor(admin) as cursor:
    cursor.execute('SELECT id, last_scanned FROM songs WHERE filename = %s', (song.filename,))
    sql_song_data = cursor.fetchone()
    
    if cursor.rowcount == 1:
      if song.id is None:
        song.id = sql_song_data['id']
      elif song.id != sql_song_data['id']:
        raise InvalidSongDataException('the given song id (%s) doesn\'t match the given filename(%s)' % (song.id, song.filename))
      
      song.last_scanned = sql_song_data['last_scanned']
      
      if song.last_scanned >= song.file_last_modified:
        logger.info('skipping file "%s" (id %s) because it was last scanned at %s after the file was last modified at %s.' %
                    (song.filename, song.id, str(song.last_scanned), str(song.file_last_modified)))
        cursor.execute('INSERT INTO song_deletion_whitelist (id) VALUES (%s)' % (int(song.id),))
        return
      
      update_song(song, cursor)
    else:
      logger.debug('got insert data from the file "%s".' % song.filename)
      insert_song(song, cursor)

    cursor.execute('INSERT INTO song_deletion_whitelist (id) VALUES (%s)' % (int(song.id), ))

    add_artist_joins(song, cursor)
    add_albums(song, cursor)
    add_genres(song, cursor)
  
  commit(admin)
  logger.info('done saving %s' % song.filename)