from api.exceptions.song_data import CatalogNotFoundException
from api.models.db_models import Catalog
from api.dao.mysql_utils import get_cursor

def get_catalog(identifier:[int, str]) -> Catalog:
  field = 'id'
  if isinstance(identifier, str):
    field = 'name'
  elif not isinstance(identifier, int):
    raise TypeError('a catalog identifier must be either an id (an int) or a name (a str).  (found "' + str(identifier) + '", a ' + str(type(identifier))[8:-2] + ' instead.)')
  
  sql_catalog = {'id': None, 'name': None, 'base_path': None}
  
  with get_cursor() as cur:
    query = 'SELECT id, name, base_path FROM catalogs WHERE ' + field + ' = %s;'
    result = cur.execute(query, (identifier, ))
    if cur.rowcount == 0:
      raise CatalogNotFoundException('no catalog with id %s was found.' % identifier)
    
    sql_catalog = cur.fetchone()
  
  return Catalog(sql_catalog['id'], sql_catalog['name'], sql_catalog['base_path'])