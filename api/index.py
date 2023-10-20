#!/usr/bin/python3.9
from os import path
import sys

base_path = path.dirname(__file__)
sys.path.append(path.realpath(base_path) + '/..')

from api.exceptions.http_base import \
  BadRequestException, \
  MethodNotAllowedException
from api.util.logger import get_logger
from api.util.http import \
  HTTPStatusCodes, \
  HTTPRequestMethods_by_name, \
  HTTPMIMETypes, \
  HTTPMIMETypes_by_name, \
  Response, \
  ResponseMessage, \
  build_http_response_from_exception, \
  get_authorization
from api.util.http_path import \
  get_and_validate_rel_path, \
  default_interface_dir, \
  path_tries
from api.util.functions import get_type_name

from inspect import signature
from urllib.parse import parse_qs

bytes_encoding = 'UTF-8'

def get_and_validate_request_method(environment:dict):
  given_method = environment['REQUEST_METHOD']
  result = HTTPRequestMethods_by_name.get(given_method, None)
  
  if result is None:
    query_string = environment['QUERY_STRING']
    rel_path = environment['REQUEST_URI']
    if len(query_string) > 0:
      rel_path = rel_path[:-1 * (len(query_string) + 1)]
    
    raise MethodNotAllowedException(given_method, rel_path)
  
  return result

default_accepted_mime_type = HTTPMIMETypes.APPLICATION_YAML
def get_accepted_mime_type(environment:dict):
  header_accept = environment.get('HTTP_ACCEPT', None)
  if header_accept is None:
    return default_accepted_mime_type
  
  return HTTPMIMETypes_by_name.get(header_accept, default_accepted_mime_type)

def get_and_validate_query_params(environment:dict):
  query_string = environment['QUERY_STRING']
  query_params = {}
  if len(query_string) > 0:
    try:
      query_params = parse_qs(query_string, keep_blank_values=True, strict_parsing=True)
    except ValueError as e:
      raise BadRequestException(str(e))
    
    query_params = {param: query_params[param][0] for param in query_params}
  
  return query_params

def get_request_body(environment:dict):
  if 'CONTENT_LENGTH' not in environment or 'wsgi.input' not in environment:
    return None
  
  # the environment variable CONTENT_LENGTH may be empty or missing
  try:
    request_body_size = int(environment.get('CONTENT_LENGTH', 0))
  except ValueError:
    return None # no request body was found
  
  return environment['wsgi.input'].read(request_body_size)

def get_contents(environment):
  request_method = get_and_validate_request_method(environment)
  rel_path_data = get_and_validate_rel_path(environment)
  query_params = get_and_validate_query_params(environment)
  body = get_request_body(environment)
  
  rel_path = rel_path_data.path_node.get_pretty_path()[len(default_interface_dir)+1:]
  if len(rel_path) == 0:
    rel_path = '/'
  
  exec_func = rel_path_data.path_node.get_request_method_func(request_method)
  bad_method_exception = MethodNotAllowedException(str(request_method), rel_path)
  if exec_func is None:
    raise bad_method_exception
  
  endpoint_sig = '%s %s' % (str(request_method).upper(), rel_path)
  try:
    sig = signature(exec_func)
    if len(sig.parameters) != 4:
      get_logger().warn('%s has the wrong number of parameters.' % (endpoint_sig, ))
      raise bad_method_exception
  except TypeError:
    get_logger().warn('%s isn\'t callable.' % (endpoint_sig, ))
    raise bad_method_exception
  
  return exec_func(preprocess_request(environment), rel_path_data.path_parameters, query_params, body)

def preprocess_request(environment:dict):
  environment['auth_object'] = get_authorization(environment)
  environment['root_path_node'] = path_tries['interface']
  # TODO auth and stuff here
  return environment

def application(environment, start_response):
  accept_mime_type = get_accepted_mime_type(environment)
  response = Response(ResponseMessage('no.'), HTTPStatusCodes.HTTP501)
  
  try:
    obj = get_contents(environment)
    if isinstance(obj, Response):
      response = obj
    else:
      response = Response(obj, HTTPStatusCodes.HTTP200, accept_mime_type)
  except Exception as e:
    get_logger().debug('caught a(n) %s: %s' % (get_type_name(e), str(e)))
    exception_traceback = e.__traceback__
    while exception_traceback is not None:
      filename = str(exception_traceback.tb_frame.f_code.co_filename)
      exception_line_number = str(exception_traceback.tb_lineno)
      get_logger().debug('  --from file ' + filename + ', line number ' + exception_line_number + '\n')
      
      exception_traceback = exception_traceback.tb_next
    
    response = build_http_response_from_exception(e)
  
  if response.get_mime_type() is None:
    response.set_mime_type(accept_mime_type)
  
  output = bytes(response.serialize(), bytes_encoding)
  status = str(response.get_status_code())
  
  headers = \
  [
    ('Content-Type', str(accept_mime_type)),
    ('Content-Length', str(len(output)))
  ]
  
  start_response(status, headers)
  
  return [output]