from api.logic.scan_catalog import scan_catalog

import sys

def launch_task():
  invalid_arg_message = 'this script needs one argument that\'s either in the form "id=<catalog id>" or "name=<catalog name>"'
  
  if len(sys.argv) != 2:
    print(invalid_arg_message)
    return
  
  arg = sys.argv[1]
  identifier = None
  if arg[0:3] == 'id=':
    identifier = int(arg[3:])
  elif arg[0:5] == 'name=':
    identifier = arg[5:]
  else:
    print(invalid_arg_message)
    return
  
  scan_catalog(identifier)

if __name__ == '__main__':
  launch_task()