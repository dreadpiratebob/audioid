from api.util.http import get_authorization

def delete(environment:dict, path_params:dict, query_params:dict, body):
  return '\n(delete)' + _generate_output(environment, path_params, query_params, body)

def get(environment:dict, path_params:dict, query_params:dict, body):
  return '\n(get)' + _generate_output(environment, path_params, query_params, body)

def patch(environment:dict, path_params:dict, query_params:dict, body):
  return '\n(patch)' + _generate_output(environment, path_params, query_params, body)

def post(environment:dict, path_params:dict, query_params:dict, body):
  return '\n(post)' + _generate_output(environment, path_params, query_params, body)

def put(environment:dict, path_params:dict, query_params:dict, body):
  return '\n(put)' + _generate_output(environment, path_params, query_params, body)

def _generate_output(environment:dict, path_params:dict, query_params:dict, body):
  output = '\nauthorization: ' + str(get_authorization(environment)) + \
           '\nraw request uri: ' + str(environment.get('REQUEST_URI', None)) + \
           '\npath params: ' + str(path_params) + \
           '\nquery params: ' + str(query_params) + \
           '\nbody: ' + str(body) + \
           '\nenv:\n'
  
  for key in environment:
    output += '  %s: %s\n' % (key, environment[key])
  
  return output