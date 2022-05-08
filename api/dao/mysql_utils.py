import pymysql

def get_cursor(admin = False):
  username = 'audioid_user'
  if admin:
    username = 'audioid_admin'

  password = 'not a good password'
  if admin:
    password = 'still not a good password'

  db = pymysql.connect(host = 'localhost', user = username, password = password, db = 'audioid', cursorclass = pymysql.cursors.DictCursor)
  return db.cursor()