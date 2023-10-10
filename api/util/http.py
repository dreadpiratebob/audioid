from api.exceptions.http_base import BaseHTTPException, BadRequestException
from api.util.functions import get_type_name, is_primitive, log_exception

from enum import Enum
from inspect import signature
from urllib.parse import quote_plus

class HTTPStatusCodes(Enum):
  def __new__(self, *args, **kwds):
    value = len(self.__members__) + 1
    obj = object.__new__(self)
    obj._value_ = value
    return obj
  
  def __init__(self, code:int, message:str):
    self._code = code
    self._message = message
  
  def __hash__(self):
    return hash(self._code)
  
  def __eq__(self, other):
    return isinstance(other, HTTPStatusCodes) and \
      self._code == other._code
  
  def __str__(self):
    return str(self._code) + ' ' + self._message
  
  def get_code(self):
    return self._code
  
  def get_message(self):
    return self._message
  
  HTTP100 = 100, 'Continue'
  HTTP102 = 102, 'Processing'
  HTTP103 = 103, 'Early Hints'
  HTTP200 = 200, 'OK'
  HTTP201 = 201, 'Created'
  HTTP202 = 202, 'Accepted'
  HTTP203 = 203, 'Non-Authoritative Information'
  HTTP204 = 204, 'No Content'
  HTTP205 = 205, 'Reset Content'
  HTTP206 = 206, 'Partial Content'
  HTTP207 = 207, 'Multi-Status'
  HTTP208 = 208, 'Already Reported'
  HTTP218 = 218, 'This is fine'
  HTTP226 = 226, 'IM Used'
  HTTP300 = 300, 'Multiple Choices'
  HTTP301 = 301, 'Moved Permanently'
  HTTP302 = 302, 'Found'
  HTTP303 = 303, 'See Other'
  HTTP304 = 304, 'Not Modified'
  HTTP305 = 305, 'Use Proxy'
  HTTP306 = 306, 'Switch Proxy'
  HTTP307 = 307, 'Temporary Redirect'
  HTTP308 = 308, 'Permanent Redirect'
  HTTP400 = 400, 'Bad Request'
  HTTP401 = 401, 'Unauthorized'
  HTTP402 = 402, 'Payment Required'
  HTTP403 = 403, 'Forbidden'
  HTTP404 = 404, 'Not Found'
  HTTP405 = 405, 'Method Not Allowed'
  HTTP406 = 406, 'Not Acceptable'
  HTTP407 = 407, 'Proxy Authentication Required'
  HTTP408 = 408, 'Request Timeout'
  HTTP409 = 409, 'Conflict'
  HTTP410 = 410, 'Gone'
  HTTP411 = 411, 'Length Required'
  HTTP412 = 412, 'Precondition Failed'
  HTTP413 = 413, 'Payload Too Large'
  HTTP414 = 414, 'URI Too Long'
  HTTP415 = 415, 'Unsupported Media Type'
  HTTP416 = 416, 'Range Not Satisfiable'
  HTTP417 = 417, 'Expectation Failed'
  HTTP418 = 418, 'I\'m a teapot'
  HTTP421 = 421, 'Misdirected Request'
  HTTP422 = 422, 'Unprocessable Entity'
  HTTP423 = 423, 'Locked'
  HTTP424 = 424, 'Failed Dependency'
  HTTP425 = 425, 'Too Early'
  HTTP426 = 426, 'Upgrade Required'
  HTTP428 = 428, 'Precondition Required'
  HTTP429 = 429, 'Too Many Requests'
  HTTP431 = 431, 'Request Header Fields Too Large'
  HTTP451 = 451, 'Unavailable For Legal Reasons'
  HTTP500 = 500, 'Internal Server Error'
  HTTP501 = 501, 'Not Implemented'
  HTTP502 = 502, 'Bad Gateway'
  HTTP503 = 503, 'Service Unavailable'
  HTTP504 = 504, 'Gateway Timeout'
  HTTP505 = 505, 'HTTP Version Not Supported'
  HTTP506 = 506, 'Variant Also Negotiates'
  HTTP507 = 507, 'Insufficient Storage'
  HTTP508 = 508, 'Loop Detected'
  HTTP510 = 510, 'Not Extended'
  HTTP511 = 511, 'Network Authentication Required'

HTTPStatusCodes_by_code = {sc.get_code(): sc for sc in HTTPStatusCodes}

class HTTPMIMETypes(Enum):
  def __new__(self, *args, **kwds):
    value = len(self.__members__) + 1
    obj = object.__new__(self)
    obj._value_ = value
    return obj
  
  def __init__(self, http_name, serializer_function_name, base_structure):
    self.http_name = http_name
    self.serializer_function_name = serializer_function_name
    self.base_structure = base_structure
  
  def __eq__(self, other):
    return isinstance(other, HTTPMIMETypes) and \
      self.http_name == other.http_name and \
      self.serializer_function_name == other.serializer_function_name and \
      self.base_structure == other.base_structure
  
  def __hash__(self):
    return (((hash(self.http_name) * 397) ^ hash(self.serializer_function_name)) * 397) ^ hash(self.base_structure)
  
  def __str__(self):
    return self.http_name
  
  APPLICATION_JSON   = 'application/json',   'to_json', '{"data": "%s"}'
  APPLICATION_X_YAML = 'application/x-yaml', 'to_yaml', 'data: %s'
  APPLICATION_XML    = 'application/xml',    'to_xml',  '<data>%s</data>'
  APPLICATION_YAML   = 'application/yaml',   'to_yaml', 'data: %s'
  TEXT_PLAIN         = 'text/plain',         None,      '%s'

HTTPMIMETypes_by_name = {x.http_name: x for x in HTTPMIMETypes} | {'*/*': HTTPMIMETypes.APPLICATION_YAML}

class HTTPRequestMethods(Enum):
  def __new__(self, *args, **kwds):
    value = len(self.__members__) + 1
    obj = object.__new__(self)
    obj._value_ = value
    return obj
  
  def __init__(self, name:str):
    self._name = name
  
  def __eq__(self, other):
    return isinstance(other, HTTPRequestMethods) and self._name == other._name
  
  def __hash__(self):
    return hash(self._name)
  
  def __str__(self):
    return self._name
  
  DELETE = 'delete'
  GET = 'get'
  PATCH = 'patch'
  POST = 'post'
  PUT = 'put'

HTTPRequestMethods_by_name = {rm.name: rm for rm in HTTPRequestMethods} | {rm.name.upper(): rm for rm in HTTPRequestMethods}

def get_authorization(environment:dict):
  return environment.get('HTTP_AUTHORIZATION', None)

class Response:
  def __init__(self, payload, status_code:HTTPStatusCodes, mime_type:HTTPMIMETypes = None, serialization_falls_back_to_fields:bool = True, use_public_fields_only:bool = True, use_base_field_in_xml = False, use_base_field_in_yaml:bool = False):
    grievances = []
    
    if payload is None:
      grievances.append('a response payload must not be None.')
    
    if not isinstance(status_code, HTTPStatusCodes):
      grievances.append('a status_code must be an HTTPStatusCode.')
    
    if mime_type is not None and not isinstance(mime_type, HTTPMIMETypes):
      grievances.append('a mime type must be an HTTPMIMEType.')
    
    if not isinstance(serialization_falls_back_to_fields, bool):
      grievances.append('the "fall back to fields" flag must be a bool.')
    
    if not isinstance(use_public_fields_only, bool):
      grievances.append('the "use public fields only" flag must be a bool.')
    
    if not isinstance(use_base_field_in_xml, bool):
      grievances.append('the "use base field in xml" flag must be a bool.')
    
    if not isinstance(use_base_field_in_yaml, bool):
      grievances.append('the "use base field in yaml" flag must be a bool.')
    
    if len(grievances) > 0:
      raise TypeError('\n'.join(grievances))
    
    self.payload = payload
    self._status_code = status_code
    self._mime_type = mime_type
    self._fall_back_to_fields = serialization_falls_back_to_fields
    self._use_public_fields_only = use_public_fields_only
    self._use_base_field_in_xml = use_base_field_in_xml
    self._use_base_field_in_yaml = use_base_field_in_yaml
  
  def __str__(self):
    mime_was_none = False
    if self._mime_type is None:
      self._mime_type = HTTPMIMETypes.TEXT_PLAIN
      mime_was_none = True
    
    result = self.serialize()
    
    if mime_was_none:
      self._mime_type = None
    
    return result
  
  def get_status_code(self):
    return self._status_code
  
  def get_mime_type(self):
    return self._mime_type
  
  def set_mime_type(self, mime_type:HTTPMIMETypes):
    if not isinstance(mime_type, HTTPMIMETypes):
      raise TypeError('a mime type must be an HTTPMIMEType.')
    
    self._mime_type = mime_type
  
  def serialize(self):
    if self._mime_type is None:
      raise ValueError('no mime type was given.')
    
    serializer_function_name = self._mime_type.serializer_function_name
    
    if serializer_function_name is not None and hasattr(self.payload, serializer_function_name):
      serializer_function = getattr(self.payload, serializer_function_name)
      
      if callable(serializer_function) and len(signature(serializer_function).parameters) == 1:
        return serializer_function(self.payload)
    
    if self._fall_back_to_fields:
      return self.serialize_by_field()
    
    data = quote_plus(str(self.payload))
    return self._mime_type.base_structure % data

  def serialize_by_field(self):
    if self._mime_type is None:
      raise ValueError('no mime type was given.')
    
    if self._mime_type == HTTPMIMETypes.APPLICATION_JSON:
      return serialize_by_field_to_json(self.payload, self._use_public_fields_only)
    
    if self._mime_type == HTTPMIMETypes.APPLICATION_XML:
      return serialize_by_field_to_xml(self.payload, self._use_public_fields_only, self._use_base_field_in_xml)
    
    if self._mime_type == HTTPMIMETypes.APPLICATION_X_YAML or self._mime_type == HTTPMIMETypes.APPLICATION_YAML:
      return serialize_by_field_to_yaml(self.payload, self._use_public_fields_only, self._use_base_field_in_yaml)
    
    if self._mime_type == HTTPMIMETypes.TEXT_PLAIN:
      return serialize_by_field_to_plain_text(self.payload, self._use_public_fields_only)
    
    return None
  
def serialize_by_field_to_json(obj, public_only:bool = True):
  if isinstance(obj, str):
    return '"' + quote_plus(obj) + '"'
  
  if isinstance(obj, (list, set, tuple)):
    return '[' + ', '.join([serialize_by_field_to_json(item, public_only) for item in obj]) + ']'
  
  if is_primitive(obj):
    return quote_plus(str(obj))
  
  json_fields = []
  fields = obj.__dict__
  for field_name in fields:
    new_name = str(field_name)
    if new_name[0] == '_':
      if public_only:
        continue
      
      new_name = new_name[1:]
    
    new_name = quote_plus(new_name)
    
    json_fields.append('"' + new_name + '": ' + serialize_by_field_to_json(fields[field_name], public_only))
  
  return '{' + ', '.join(json_fields) + '}'

def serialize_by_field_to_xml(obj, public_only:bool = True, use_base_field:bool = False):
  if isinstance(obj, (list, set, tuple)):
    return ''.join(['<item>' + serialize_by_field_to_xml(item, public_only, True) + '</item>' for item in obj])
  
  if is_primitive(obj):
    return quote_plus(str(obj))
  
  outter_tag = get_type_name(obj, True)
  result = ''
  if use_base_field:
    result = '<' + outter_tag + '>'
  
  fields = obj.__dict__
  for field_name in fields:
    new_name = str(field_name)
    if new_name[0] == '_':
      if public_only:
        continue
      
      new_name = new_name[1:]
    
    new_name = quote_plus(new_name)
    result += '<' + new_name + '>' + serialize_by_field_to_xml(fields[field_name], public_only) + '</' + new_name + '>'
  
  if use_base_field:
    result += '</' + outter_tag + '>'
  
  return result

yaml_indent = '  '
def serialize_by_field_to_yaml(obj, public_only:bool = True, use_base_field:bool = False, indent:int = 0):
  if isinstance(obj, str):
    return '"' + quote_plus(obj) + '"'
  
  if isinstance(obj, (list, set, tuple)):
    result = ''
    for item in obj:
      result += '\n' + yaml_indent*indent + '- ' + serialize_by_field_to_yaml(item, public_only, True, indent+1)
    return result
  
  if is_primitive(obj):
    return quote_plus(str(obj))
  
  result = ''
  if use_base_field:
    result += get_type_name(obj, True) + ':'
    indent += 1
  
  fields = obj.__dict__
  for field_name in fields:
    new_name = str(field_name)
    if new_name[0] == '_':
      if public_only:
        continue
      
      new_name = new_name[1:]
    
    new_name = quote_plus(new_name)
    result += '\n' + yaml_indent*indent + new_name + ': ' + serialize_by_field_to_yaml(fields[field_name], public_only, False, indent+1)
  
  if not use_base_field and len(result) > 0 and result[0] == '\n':
    result = result[1:]
  
  return result.replace(' \n', '\n')

plain_text_indent = '  '
def serialize_by_field_to_plain_text(obj, public_only:bool = True, use_base_field:bool = True, indent:int = 0):
  if isinstance(obj, str):
    return '"' + quote_plus(str(obj)) + '"'
  
  if isinstance(obj, (list, set)):
    start = '[' if isinstance(obj, list) else '{'
    end = ']' if isinstance(obj, list) else '}'
    
    base_str = plain_text_indent*indent + start + '\n' + plain_text_indent*(indent+1) + '%s\n' + plain_text_indent*indent + end
    list_str = ('\n' + plain_text_indent*(indent+1)).join([serialize_by_field_to_plain_text(item, public_only, use_base_field, indent + 2) for item in obj])
    return base_str % (list_str, )
  
  if isinstance(obj, dict):
    list_str = ('\n' + plain_text_indent*(indent+1)).join([str(key) + ': ' + serialize_by_field_to_plain_text(obj[key], public_only, use_base_field, indent + 2) for key in obj])
    return plain_text_indent*indent + '{\n' + list_str + '\n' + plain_text_indent*indent + '}'
  
  if is_primitive(obj):
    return quote_plus(str(obj))
  
  outer = get_type_name(obj, True)
  
  result = ''
  if use_base_field:
    result += outer + ':'
    indent += 1
  
  fields = obj.__dict__
  for field_name in fields:
    new_name = str(field_name)
    if new_name[0] == '_':
      if public_only:
        continue
      
      new_name = new_name[1:]
    
    new_name = quote_plus(new_name)
    result += '\n' + plain_text_indent * indent + new_name + ': ' + serialize_by_field_to_plain_text(fields[field_name], public_only, True, indent + 1)
  
  return result

class ResponseMessage:
  def __init__(self, message:str):
    if not isinstance(message, str):
      raise TypeError('give me a string for an error message, nub.')
    
    self.message = message
  
  def __str__(self):
    return str(self.message)

def build_http_response_from_exception(exception:Exception, mime_type:HTTPMIMETypes = None):
  grievances = []
  
  if not isinstance(exception, Exception):
    grievances.append('an exception must be an Exception.')
  
  if mime_type is not None and not isinstance(mime_type, HTTPMIMETypes):
    grievances.append('a mime_type must be an HTTPMIMEType.')
  
  if len(grievances) > 0:
    raise TypeError('\n'.join(grievances))
  
  if not isinstance(exception, BaseHTTPException):
    log_exception(exception)
    return Response(ResponseMessage("an internal error occurred."), HTTPStatusCodes.HTTP500, mime_type)
  
  return Response(ResponseMessage(exception.get_message()), HTTPStatusCodes_by_code[exception.get_status()], mime_type)

def get_param(key:str, params:dict, parse_func, type_name:str, required:bool = False, param_type:str = 'query', default_value = None, return_error_message:bool = False):
  if key not in params:
    if required:
      if return_error_message:
        return default_value, BadRequestException('the %s parameter called "%s" is required and was missing.' % (param_type, key))
      else:
        raise BadRequestException('the %s parameter called "%s" is required and was missing.' % (param_type, key))
    
    return default_value, None
  
  try:
    return parse_func(params[key]), None
  except ValueError:
    if return_error_message:
      return None, BadRequestException('the %s "%s" couldn\'t be parsed as %s.' % (key, params[key], type_name))
    else:
      raise BadRequestException('the %s "%s" couldn\'t be parsed as %s.' % (key, params[key], type_name))