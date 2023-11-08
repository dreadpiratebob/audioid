from enum import Enum
from unidecode import unidecode

_diacritic_removal_special_cases = \
{
  'KoЯn': 'Korn'
}
def get_search_text_from_raw_text(raw_text:str) -> tuple[str, str, str]:
  lcase = raw_text.lower()
  
  if raw_text in _diacritic_removal_special_cases:
    no_diacritics = _diacritic_removal_special_cases[raw_text]
  else:
    no_diacritics = unidecode(raw_text)
  
  lcase_no_diacritics = no_diacritics.lower()
  
  return lcase, no_diacritics, lcase_no_diacritics

def get_type_name(value:any, class_only:bool = False) -> str:
  start_index = 8
  if isinstance(value, Enum):
    start_index = 7
  
  result = str(type(value))[start_index:-2]
  
  if not class_only:
    return result
  
  return result[result.rfind('.')+1:]

def hash_dict(d:dict) -> int:
  result = 0
  
  sorted_keys = [key for key in d]
  sorted_keys.sort()
  for key in sorted_keys:
    result = (((result*397) ^ hash(key))*397) ^ hash(d[key])
  
  return result

def hash_list_or_tuple(obj:(list, tuple)) -> int:
  if not isinstance(obj, (list, tuple)):
    raise TypeError('to hash a list or tuple, you have to start with a list or tuple.')
  
  result = 0
  
  for item in obj:
    new_hash = 0
    if isinstance(item, (list, tuple)):
      new_hash = hash_list_or_tuple(item)
    elif isinstance(item, dict):
      new_hash = hash_dict(item)
    else:
      new_hash = hash(item)
    
    result = result * 397 ^ new_hash
  
  return result

def is_iterable(obj:any) -> bool:
  return hasattr(obj, '__iter__')

def is_primitive(obj:any) -> bool:
  return not hasattr(obj, '__dict__')

def parse_bool(obj:any, throw_on_failure:bool = True, default_value:bool = False) -> bool:
  if isinstance(obj, bool):
    return obj
  elif isinstance(obj, str):
    text = obj.lower()
    if text == 'true':
      return True
    if text == 'false':
      return False
  elif isinstance(obj, (int, float)):
    return obj != 0
  
  if throw_on_failure:
    raise ValueError('"%s" (a(n) %s) isn\'t parsable as a bool.' % (str(obj), get_type_name(obj)))
  else:
    return default_value