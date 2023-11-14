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

class OrderByCol:
  def __init__(self, col:OrderColName, direction:OrderDirection):
    self.col = col
    self.direction = direction

def get_order_clause(order_bys:list[OrderByCol]) -> str:
  return ', '.join(['%s %s' % (ob.col.column_name, ob.direction.value) for ob in order_bys])