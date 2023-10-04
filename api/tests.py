from api.exceptions.http_base import BadRequestException, NotFoundException
from api.index import base_path
from api.util.http_path import \
  PathData, \
  PathNode, \
  get_path_trie, \
  get_and_validate_rel_path, \
  path_param_folder_name_re, \
  path_tries
from api.util.http import \
  HTTPRequestMethods, \
  HTTPStatusCodes, \
  HTTPMIMETypes, \
  ResponseMessage, \
  build_http_response_from_exception, \
  serialize_by_field_to_json, \
  serialize_by_field_to_xml, \
  serialize_by_field_to_yaml, \
  serialize_by_field_to_plain_text

from os import path
from urllib.parse import quote_plus

import unittest

class Dummy:
  def __init__(self, name:str, public_data, private_data):
    self.name = name
    self.public_data = public_data
    self._private_data = private_data

class SerToJSONTests(unittest.TestCase):
  def test_primitive(self):
    value = 2
    
    expected = '2'
    actual   = serialize_by_field_to_json(value)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_only(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '{"name": "%s", "public_data": "%s"}' % (name, public)
    actual   = serialize_by_field_to_json(value)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_private(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '{"name": "%s", "public_data": "%s", "private_data": "%s"}' % (name, public, quote_plus(private))
    actual   = serialize_by_field_to_json(value, False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)

    expected = '{"name": "%s", "public_data": ["a", "b", "c", "d"]}' % (name, )
    actual = serialize_by_field_to_json(value)

    self.assertEqual(expected, actual)

class SerToXMLTests(unittest.TestCase):
  def test_primitive(self):
    value = 2
    
    expected = '2'
    actual   = serialize_by_field_to_xml(value)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_only(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '<Dummy><name>%s</name><public_data>%s</public_data></Dummy>' % (name, public)
    actual   = serialize_by_field_to_xml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_private(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '<Dummy><name>%s</name><public_data>%s</public_data><private_data>%s</private_data></Dummy>' % (name, public, quote_plus(private))
    actual   = serialize_by_field_to_xml(value, False, True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '<Dummy><name>%s</name><public_data>%s</public_data></Dummy>' % (name, ''.join(['<item>' + item + '</item>' for item in public]))
    actual = serialize_by_field_to_xml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)

class SerToYAMLTests(unittest.TestCase):
  def test_primitive(self):
    value = 2
    
    expected = '2'
    actual   = serialize_by_field_to_yaml(value)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_only(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: "%s"' % (name, public)
    actual   = serialize_by_field_to_yaml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_private(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)

    expected = 'Dummy:\n  name: "%s"\n  public_data: "%s"\n  private_data: "%s"' % (name, public, quote_plus(private))
    actual   = serialize_by_field_to_yaml(value, False, True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data:\n    - "a"\n    - "b"\n    - "c"\n    - "d"' % (name, )
    actual = serialize_by_field_to_yaml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_simple_message(self):
    message = 'thing'
    rm = ResponseMessage(message)
    
    expected = 'message: "%s"' % (message, )
    actual = serialize_by_field_to_yaml(rm)
    
    self.assertEqual(expected, actual)

class SerToTextTests(unittest.TestCase):
  def test_primitive(self):
    value = 2
    
    expected = '2'
    actual   = serialize_by_field_to_plain_text(value)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_only(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: "%s"' % (name, public)
    actual   = serialize_by_field_to_plain_text(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_public_private(self):
    name = 'dummy.'
    public = 'asdf'
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: "%s"\n  private_data: "%s"' % (name, public, quote_plus(private))
    actual   = serialize_by_field_to_plain_text(value, False, True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: "%s"' % (name, quote_plus(str(public)))
    actual = serialize_by_field_to_plain_text(value, use_base_field=True)
    
    self.assertEqual(expected, actual)

class BuildResponseFromExceptionTests(unittest.TestCase):
  def test_404_not_found(self):
    message = 'not found'
    error = NotFoundException(message)
    response = build_http_response_from_exception(error, HTTPMIMETypes.APPLICATION_YAML)
    
    expected = 'message: "%s"' % (message.replace(' ', '+'), )
    actual = response.serialize()
    
    self.assertEqual(expected, actual)

class StatusCodeTests(unittest.TestCase):
  def test_buildability(self):
    code = HTTPStatusCodes.HTTP418
    
    self.assertEqual(code.get_code(), 418)
    self.assertEqual(code.get_message(), 'I\'m a teapot')

unittest_base_path = 'unittest_interface'
class PathTrieTests(unittest.TestCase):
  def test_unittest_base_happy_path(self):
    expected = self._build_unittest_interface_trie()
    actual = get_path_trie(unittest_base_path)
    
    self._compare_path_node_trees(expected, actual)
    self.assertIsNone(actual.get_parent())
    self.assertIsNotNone(actual.get_request_method_func(HTTPRequestMethods.GET))
  
  def test_default_base_path_has_get(self):
    node = get_path_trie('interface')
    self.assertIsNotNone(node.get_request_method_func(HTTPRequestMethods.GET))
  
  def _build_unittest_interface_trie(self):
    root = PathNode(None, base_path, 'unittest_interface')
    
    a_base_folder = PathNode(root, base_path + root.get_raw_path(), 'a_base_folder')
    long_path_start = PathNode(a_base_folder, base_path + a_base_folder.get_raw_path(), 'long_path_start')
    no_index = PathNode(a_base_folder, base_path + a_base_folder.get_raw_path(), 'no_index')
    path_var = PathNode(a_base_folder, base_path + a_base_folder.get_raw_path(), 'path_var')
    __some_var__int__ = PathNode(path_var, base_path + path_var.get_raw_path(), '__some_var__int__')
    debug = PathNode(path_var, base_path + path_var.get_raw_path(), 'debug')
    no_index = PathNode(path_var, base_path + path_var.get_raw_path(), 'no_index')
    
    return root
  
  def _compare_path_node_trees(self, expected:PathNode, actual:PathNode):
    cur_expected = expected
    while cur_expected.get_parent() is not None:
      cur_expected = cur_expected.get_parent()
    
    cur_actual = actual
    while cur_actual.get_parent() is not None:
      cur_actual = cur_actual.get_parent()
    
    expected_q = [cur_expected]
    actual_q = [cur_actual]
    while len(expected_q) > 0:
      self.assertEqual(len(expected_q), len(actual_q))
      
      cur_expected = expected_q.pop(0)
      cur_actual = actual_q.pop(0)
      
      print('expected: ' + cur_expected.get_raw_path())
      print('actual:   ' + cur_actual.get_raw_path())
      print()
      
      self.assertEqual(cur_expected, cur_actual)
      for rm in HTTPRequestMethods:
        self.assertEqual(cur_expected.get_request_method_func(rm), cur_actual.get_request_method_func(rm))
      
      exp_children = [child for child in cur_expected.get_children()]
      exp_children.sort(key = lambda child: child.get_raw_folder_name())
      expected_q += exp_children
      
      act_children = [child for child in cur_actual.get_children()]
      act_children.sort(key = lambda child: child.get_raw_folder_name())
      actual_q += act_children

request_uri_key = 'REQUEST_URI'
query_string_key = 'QUERY_STRING'
end_path = 'index.py'
path_tries[unittest_base_path] = get_path_trie(unittest_base_path)
class RelPathTests(unittest.TestCase):
  def test_base_happy_path(self):
    folder_name = 'a_base_folder'
    input_path = '/%s' % folder_name
    env = {request_uri_key: input_path, query_string_key: ''}
    
    expected = PathData(path_tries[unittest_base_path][folder_name], {}, None)
    actual = get_and_validate_rel_path(env, unittest_base_path)
    
    self.assertEqual(PathData, type(actual))
    self.assertEqual(expected, actual)
  
  def test_path_param_happy_path(self):
    vars = {'some_var': '9'}
    folders = ['a_base_folder', 'path_var', 'some_var']
    input_path = ('/' + '/'.join(folders)).replace('some_var', '9')
    env = {request_uri_key: input_path, query_string_key: ''}
    
    expected_node = path_tries[unittest_base_path]
    for folder in folders:
      expected_node = expected_node[folder]
    
    expected = PathData(expected_node, {'some_var': 9}, None)
    actual = get_and_validate_rel_path(env, unittest_base_path)
    
    self.assertEqual(PathData, type(actual))
    self.assertEqual(expected, actual)
  
  def test_almost_ambiguous_happy_path(self):
    folders = ['a_base_folder', 'path_var', 'debug']
    input_path = '/' + '/'.join(folders)
    env = {request_uri_key: input_path, query_string_key: ''}
    
    expected_node = path_tries[unittest_base_path]
    for folder in folders:
      expected_node = expected_node[folder]
    
    expected = PathData(expected_node, {}, None)
    actual = get_and_validate_rel_path(env, unittest_base_path)
    
    self.assertEqual(PathData, type(actual))
    self.assertEqual(expected, actual)
  
  def test_no_index_sad_path(self):
    input_path = '/a_base_folder/no_index'
    env = {request_uri_key: input_path, query_string_key: ''}
    
    found_error = False
    try:
      get_and_validate_rel_path(env, unittest_base_path)
    except Exception as e:
      found_error = True
      
      self.assertEqual(NotFoundException, type(e))
    
    self.assertTrue(found_error)
  
  def test_no_index_next_to_path_var_sad_path(self):
    input_path = '/a_base_folder/path_var/no_index'
    env = {request_uri_key: input_path, query_string_key: ''}
    
    found_error = False
    try:
      get_and_validate_rel_path(env, unittest_base_path)
    except Exception as e:
      found_error = True
      
      self.assertEqual(BadRequestException, type(e))
    
    self.assertTrue(found_error)
  
  def test_long_path_sad_path(self):
    input_path = '/a_base_folder/long_path_start/this/path/is/too/long'
    env = {request_uri_key: input_path, query_string_key: ''}
    
    found_error = False
    try:
      get_and_validate_rel_path(env, unittest_base_path)
    except Exception as e:
      found_error = True
      
      self.assertEqual(NotFoundException, type(e))
    
    self.assertTrue(found_error)
  
  def test_functions_exist(self):
    node = path_tries[unittest_base_path]['a_base_folder']
    
    self.assertIsNotNone(node.get_request_method_func(HTTPRequestMethods.GET))
  
  def test_subdir_path_param_regex_matches_happy_path(self):
    subdir_name = '__song_id__int__'
    
    self.assertIsNotNone(path_param_folder_name_re.match(subdir_name))

if __name__ == '__main__':
  unittest.main()