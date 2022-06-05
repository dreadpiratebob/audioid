import pymysql

user_db_conn  = pymysql.connect(host = 'localhost', user = 'audioid_user',  password = 'not a good password',                     db = 'audioid', charset='utf8mb4', cursorclass = pymysql.cursors.DictCursor)
admin_db_conn = pymysql.connect(host = 'localhost', user = 'audioid_admin', password = 'this is not a good password nor is this', db = 'audioid', charset='utf8mb4', cursorclass = pymysql.cursors.DictCursor)

def get_cursor(admin = False):
  conn = user_db_conn
  if admin:
    conn = admin_db_conn
  
  return conn.cursor()

def commit(admin = False):
  conn = user_db_conn
  if admin:
    conn = admin_db_conn
  
  conn.commit()