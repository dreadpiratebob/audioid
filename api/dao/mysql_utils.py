import pymysql

from api.util.config import get_config_value, set_config_value
from api.util.logger import get_logger

host       = get_config_value('db_host')
user_name  = get_config_value('db_user')
user_pw    = get_config_value('db_user_password')
admin_name = get_config_value('db_user')
admin_pw   = get_config_value('db_user_password')
db_name    = get_config_value('db_name')
charset    = get_config_value('db_charset')

missing_user_conn_info  = False
missing_admin_conn_info = False

if host is None:
  missing_user_conn_info  = True
  missing_admin_conn_info = True

if user_name is None:
  missing_user_conn_info = True

if user_pw is None:
  missing_user_conn_info = True

if admin_name is None:
  missing_admin_conn_info = True

if admin_pw is None:
  missing_admin_conn_info = True

if db_name is None:
  missing_user_conn_info  = True
  missing_admin_conn_info = True

if charset is None:
  missing_user_conn_info  = True
  missing_admin_conn_info = True


user_db_conn  = None
admin_db_conn = None

if missing_user_conn_info:
  get_logger().warn('since some db connection info is missing, the user connection won\'t be loaded and won\'t work.')
else:
  user_db_conn = pymysql.connect(host = 'localhost', user = 'audioid_user',  password = 'squiggly music',        db = 'audioid', charset='utf8mb4', cursorclass = pymysql.cursors.DictCursor)

if missing_admin_conn_info:
  get_logger().warn('since some db connection info is missing, the admin connection won\'t be loaded and won\'t work.')
else:
  admin_db_conn = pymysql.connect(host = 'localhost', user = 'audioid_admin', password = 'hey look - a password', db = 'audioid', charset='utf8mb4', cursorclass = pymysql.cursors.DictCursor)

def get_cursor(admin:bool = False) -> pymysql.Connection:
  conn = user_db_conn
  if admin:
    conn = admin_db_conn
  
  return conn.cursor()

def commit(admin:bool = False):
  conn = user_db_conn
  if admin:
    conn = admin_db_conn
  
  conn.commit()