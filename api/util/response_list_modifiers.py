from enum import Enum

class FilterInfo:
  def __init__(self, id:int, name:str, has_wildcards:bool, is_case_sensitive:bool, matches_diacritics:bool, filter_on_null:bool):
    self.id = id
    self.name = name
    self.name_has_wildcards = has_wildcards
    self.name_is_case_sensitive = is_case_sensitive
    self.name_matches_diacritics = matches_diacritics
    self.filter_on_null = filter_on_null
  
  def __eq__(self, other):
    if not isinstance(other, type(self)):
      return False
    
    for field_name in self.__dict__:
      if self.__dict__[field_name] != other.__dict__[field_name]:
        return False
    
    return True
  
  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __hash__(self):
    result = 0
    
    for field_name in self.__dict__:
      result = (result*397)*hash(self.__dict__[field_name])
    
    return result
  
  def clone(self):
    return FilterInfo(self.id, self.name, self.name_has_wildcards, self.name_is_case_sensitive, self.name_matches_diacritics, self.filter_on_null)

default_filter_info = FilterInfo(None, None, False, True, True, False)

class OrderColName(Enum):
  def __new__(self, *args, **kwds):
    value = len(self.__members__) + 1
    obj = object.__new__(self)
    obj._value_ = value
    return obj
  
  def __init__(self, column_name:str, description:str):
    self.column_name = column_name
    self.description = description

class OrderDirection(Enum):
  ASCENDING = 'ASC'
  DESCENDING = 'DESC'

def get_order_direction(input:str) -> OrderDirection:
  input = input.lower()
  
  if input in (OrderDirection.ASCENDING.value.lower(), 'ascending'):
    return OrderDirection.ASCENDING
  
  if input in (OrderDirection.DESCENDING.value.lower(), 'descending'):
    return OrderDirection.DESCENDING
  
  raise ValueError('the value "%s" can\'t be parsed as an order direction.' % (str(input), ))

class OrderByCol:
  def __init__(self, col:OrderColName, direction:OrderDirection):
    self.col = col
    self.direction = direction
  
  def __eq__(self, other):
    return isinstance(other, OrderByCol) and \
      self.col == other.col and \
      self.direction == other.direction
  
  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __hash__(self):
    return (hash(self.col)*397) ^ hash(self.direction)
  
  def __str__(self):
    return '%s %s' % (self.col.column_name, self.direction.value)

def get_order_parser(cols:type(OrderColName), cols_by_name = None):
  def parse_order(input:str) -> list[OrderByCol]:
    result = []
    
    _cols_by_name = cols_by_name
    if _cols_by_name is None:
      _cols_by_name = {col.column_name: col for col in cols}
    
    tokens = input.split(',')
    if len(tokens) < 0:
      raise ValueError('no column names were found.')
    
    for token in tokens:
      if token[0] == ' ':
        token = token[1:]
      
      pieces = token.split(' ')
      if len(pieces) > 2:
        raise ValueError('the order piece "%s" has too many spaces; a column name can\'t have spaces, so each piece should have at most one space.' % (token, ))
      
      if pieces[0] not in _cols_by_name:
        raise ValueError('"%s" isn\'t a valid column name; valid column names are %s.' % (pieces[0], ', '.join([col.column_name for col in cols]), ))
      
      _col = _cols_by_name[pieces[0]]
      _dir = OrderDirection.ASCENDING
      if len(pieces) == 2:
        _dir = get_order_direction(pieces[1])
      
      result.append(OrderByCol(_col, _dir))
    
    return result
  
  return parse_order

def get_order_clause(order_bys:[list[OrderByCol], tuple[OrderByCol]]) -> str:
  return ', '.join(['%s %s' % (ob.col.column_name, ob.direction.value) for ob in order_bys])

class PageInfo:
  def __init__(self, page_number:int, page_size:int):
    grievances = []
    
    if not isinstance(page_number, int):
      grievances.append('a page number must be an integer.')
    
    if not isinstance(page_size, int):
      grievances.append('a page size must be an integer.')
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    if page_number < 1:
      grievances.append('a page number must be at least 1.')
    
    if page_size < 1:
      grievances.append('a page size must be at least 1.')
    
    if len(grievances) > 0:
      raise ValueError('\n'.join(grievances))
    
    self.page_number = page_number
    self.page_size   = page_size
  
  def __eq__(self, other):
    if not isinstance(other, type(self)):
      return False
    
    for field_name in self.__dict__:
      if self.__dict__[field_name] != other.__dict__[field_name]:
        return False
    
    return True
  
  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __hash__(self):
    result = 0
    
    for field_name in self.__dict__:
      result = result*397 ^ hash(self.__dict__[field_name])
    
    return result
  
  def __str__(self):
    return 'LIMIT %s OFFSET %s' % (self.page_size, (self.page_number - 1)*self.page_size)

def parse_page_size(input:str) -> int:
  input = input.lower()
  
  if input == 'all':
    return None
  
  return int(input)