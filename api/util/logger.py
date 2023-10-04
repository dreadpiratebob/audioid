import datetime
import os.path
import re

from enum import Enum

_log_dir = '/var/log/audioid/'

class LogLevel(Enum):
  DEBUG = ('debug', 0)
  INFO  = ('info', 1)
  WARN  = ('warn', 2)
  ERROR = ('error', 3)

class Logger:
  def __init__(self, log_level:LogLevel, log_dir:str = None):
    grievances = []
    
    if not isinstance(log_level, LogLevel):
      grievances.append('a log level must be a LogLevel.')
    
    if log_dir is not None and not isinstance(log_dir, str):
      grievances.append('a dir name must be a str.')
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    if log_dir is None:
      log_dir = _log_dir
    
    log_dir = log_dir.replace('\\', '/')
    
    if log_dir[-1] != '/':
      log_dir += '/'
    
    self._log_level = log_level
    self._log_dir   = log_dir
  
  def debug(self, message):
    self.log(LogLevel.DEBUG, message)
  
  def info(self, message):
    self.log(LogLevel.INFO, message)
  
  def warn(self, message):
    self.log(LogLevel.WARN, message)
  
  def error(self, message):
    self.log(LogLevel.ERROR, message)
  
  def log(self, log_level, message):
    if log_level.value[1] < self._log_level.value[1]:
      return
    
    bad_unicode_chars = u'[\udc00-\udfff]'
    message = re.sub(bad_unicode_chars, '?', message)
    
    now = datetime.datetime.utcnow()
    fmt_msg = '%s [%s]: %s' % (str(now), log_level.value[0], str(message))
    print(fmt_msg)
    
    if not os.path.exists(_log_dir):
      os.makedirs(_log_dir)
    
    with open(self._log_dir + 'out.log', 'a+') as file_object:
      file_object.write("\n" + fmt_msg)

loggers = {LogLevel.DEBUG: {}, LogLevel.INFO: {}, LogLevel.WARN: {}, LogLevel.ERROR: {}}
def get_logger(log_level = LogLevel.DEBUG, log_dir = _log_dir):
  global loggers
  
  if log_dir in loggers[log_level].keys():
    return loggers[log_level][log_dir]
  
  logger = Logger(log_level, log_dir)
  loggers[log_level][log_dir] = logger
  
  return logger