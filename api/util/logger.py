import datetime
import re

from enum import Enum

class LogLevel(Enum):
  DEBUG = ('debug', 0)
  INFO  = ('info', 1)
  WARN  = ('warn', 2)
  ERROR = ('error', 3)

class Logger:
  def __init__(self, log_level, log_file = None):
    self.log_level = log_level
    self.log_file  = str(log_file)
  
  def debug(self, message):
    self.log(LogLevel.DEBUG, message)
  
  def info(self, message):
    self.log(LogLevel.INFO, message)
  
  def warn(self, message):
    self.log(LogLevel.WARN, message)
  
  def error(self, message):
    self.log(LogLevel.ERROR, message)
  
  def log(self, log_level, message):
    if log_level.value[1] < self.log_level.value[1]:
      return
    
    bad_unicode_chars = u'[\udc00-\udfff]'
    message = re.sub(bad_unicode_chars, '?', message)
    
    now = datetime.datetime.utcnow()
    fmt_msg = '%s [%s]: %s' % (str(now), log_level.value[0], str(message))
    print(fmt_msg)
    
    with open(self.log_file, 'a+') as file_object:
      file_object.write("\n" + fmt_msg)

loggers = {LogLevel.DEBUG: {}, LogLevel.INFO: {}, LogLevel.WARN: {}, LogLevel.ERROR: {}}
def get_logger(log_level = LogLevel.DEBUG, log_file = '/var/log/audioid/out.log'):
  global loggers
  
  if log_file in loggers[log_level].keys():
    return loggers[log_level][log_file]
  
  logger = Logger(log_level, log_file)
  loggers[log_level][log_file] = logger
  
  return logger