import sys
sys.path.insert(1, '../')

from exceptions import CatalogNotFoundException
from models.catalog import Catalog
from dao.mysql_utils import get_cursor

def get_catalog_by_id(id):
  return get_catalog('id', id)

def get_catalog_by_name(name):
  return get_catalog('name', name)

def get_catalog(field, identifier):
  sql_catalog = {'id': None, 'name': None, 'base_path': None}
  
  with get_cursor() as cur:
    query = 'SELECT id, name, base_path FROM catalogs WHERE ' + str(field) + ' = %s;'
    result = cur.execute(query, (identifier, ))
    if cur.rowcount == 0:
      raise CatalogNotFoundException('no catalog with id %s was found.' % id)
    
    sql_catalog = cur.fetchone()
  
  return Catalog(sql_catalog['id'], sql_catalog['name'], sql_catalog['base_path'])