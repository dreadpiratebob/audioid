from api.util.logger import get_logger

from enum import Enum
from os import path

def get_type_name(value, class_only=False):
  start_index = 8
  if isinstance(value, Enum):
    start_index = 7
  
  result = str(type(value))[start_index:-2]
  
  if not class_only:
    return result
  
  return result[result.rfind('.')+1:]

def hash_dict(d:dict):
  result = 0
  
  sorted_keys = [key for key in d]
  sorted_keys.sort()
  for key in sorted_keys:
    result = (((result*397) ^ hash(key))*397) ^ hash(d[key])
  
  return result

def is_iterable(value):
  return hasattr(value, '__iter__')

def is_primitive(obj):
  return not hasattr(obj, '__dict__')

def log_exception(exception:Exception):
  exception_type = str(type(exception))[8:-2]
  message = 'caught an exception of type ' + exception_type + '.\n'
  message += 'exception message: ' + str(exception) + '\n'
  message += 'stack trace:\n'
  
  exception_traceback = exception.__traceback__
  while exception_traceback is not None:
    filename = str(exception_traceback.tb_frame.f_code.co_filename)
    exception_line_number = str(exception_traceback.tb_lineno)
    message += '--from file ' + filename + ', line number ' + exception_line_number + '\n'
    
    exception_traceback = exception_traceback.tb_next
  
  get_logger().error(message)