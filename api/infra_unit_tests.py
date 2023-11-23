from api.util.config import load_config, get_config_value, set_config_value
load_config('test')

from api.exceptions.http_base import BadRequestException, NotFoundException
from api.index import base_path
from api.util.audioid.songs import GetSongsQueryParams
from api.util.functions import get_search_text_from_raw_text, hash_dict
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
from api.util.response_list_modifiers import \
  OrderColName, OrderDirection, OrderByCol, \
  get_order_clause, get_order_parser

from urllib.parse import quote_plus

import unittest

class Dummy:
  def __init__(self, name:str, public_data:any, private_data:any):
    self.name = name
    self.public_data = public_data
    self._private_data = private_data
  
  def __eq__(self, other:any) -> bool:
    if type(self) != type(other):
      return False
    
    for key in other.__dict__:
      if key not in self.__dict__:
        return False
    
    for key in self.__dict__:
      if key not in other.__dict__:
        return False
      
      if self.__dict__[key] != other.__dict__[key]:
        return False
    
    return True
  
  def __hash__(self) -> int:
    result = 0
    
    for value in self.__dict__.values():
      hash_val = 0
      if isinstance(value, dict):
        hash_val = hash_dict(value)
      else:
        hash_val = hash(value)
      
      result = (result*397) ^ hash_val
    
    return result
  
  def __str__(self) -> str:
    return 'Dummy "%s": %s' % (self.name, str(self.public_data))

class Joiner:
  def __init__(self, thing1:any, thing2:any):
    self.thing1 = thing1
    self.thing2 = thing2
  
  def __eq__(self, other:any) -> bool:
    return isinstance(other, Joiner) and \
      self.thing1 == other.thing1 and \
      self.thing2 == other.thing2
  
  def __ne__(self, other:any) -> bool:
    return not self.__eq__(other)
  
  def __hash__(self) -> int:
    return (hash(self.thing1)*397) ^ hash(self.thing2)
  
  def __str__(self) -> str:
    return 'thing1: %s\nthing2: %s' % (str(self.thing1), str(self.thing2))

recursively_joined_object_1 = Dummy('recursive_test_1.', [], 1)
recursively_joined_object_2 = Dummy('recursive_test_2.', ["!"], 2)
joiner = Joiner(recursively_joined_object_1, recursively_joined_object_2)

recursively_joined_object_1.public_data.append(joiner)
recursively_joined_object_2.public_data.append(joiner)

primitive_dummy = Dummy('primitive dummy.', 'a', 'b')

two_same_level_references = Dummy('two same-level references.', primitive_dummy, primitive_dummy)

class ConfigTests(unittest.TestCase):
  def test_get_value(self):
    expected = 'some_val'
    actual   = get_config_value('some_key')
    
    self.assertEqual(expected, actual)
  
  def test_set_value(self):
    key = 'set_key'
    val = 2
    
    set_config_value(key, val)
    
    expected = val
    actual   = get_config_value(key)
    self.assertEqual(expected, actual)

class CharEncodingTests(unittest.TestCase):
  # self.assertEqual somehow makes it so that ('š', ) == ('Š', ) is true,  \-:
  # so using self.assertEqual to compare those two tuples makes it so that tests
  # don't fail when they should.
  
  def test_basic_letters(self):
    input = 'letters'
    
    expected = (input, input, input)
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_lcase_diacritics(self):
    input = 'ňě'
    
    expected = (input, 'ne', 'ne')
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_2case_diacritics(self):
    input = 'Šiňě'
    
    expected = ('šiňě', 'Sine', 'sine')
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_korn(self):
    input = 'KoЯn'

    expected = ('koяn', 'Korn', 'korn')
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_mandarin(self):
    input = '为什么'
    
    expected = ('为什么', 'Wei Shen Me ', 'wei shen me ')
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_only_numbers(self):
    input = '1234'
    
    expected = (input, input, input)
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_only_punctuation(self):
    input = '>.<'
    
    expected = (input, input, input)
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)
  
  def test_letters_and_punctuation(self):
    input = 'Ó_Ò'
    
    expected = ('ó_ò', 'O_O', 'o_o')
    actual   = get_search_text_from_raw_text(input)
    
    self.assertTrue(expected == actual)

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
  
  def test_object_with_list_of_primitives(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)

    expected = '{"name": "%s", "public_data": ["a", "b", "c", "d"]}' % (name, )
    actual = serialize_by_field_to_json(value)

    self.assertEqual(expected, actual)
  
  def test_object_with_list_of_objects(self):
    name = 'dummy.'
    public = [Dummy('a', 'pub_a', None), Dummy('b', 'pub_b', None), Dummy('c', 'pub_c', None), Dummy('d', 'pub_d', None)]
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected_public = '[%s]' % (', '.join(['{"name": "%s", "public_data": "%s"}' % (item.name, item.public_data) for item in public]), )
    
    expected = '{"name": "%s", "public_data": %s}' % (name, expected_public)
    actual = serialize_by_field_to_json(value)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_tuple(self):
    name = 'dummy.'
    public = ('a', 'b', 'c', 'd')
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '{"name": "%s", "public_data": [%s]}' \
                % (name, ', '.join('"%s"' % (item, ) for item in public))
    actual = serialize_by_field_to_json(value)
    
    self.assertEqual(expected, actual)

  def test_dict_of_primitives(self):
    obj = {'a': 1, 'b': 2, 'c': 3}
    
    expected = '{%s}' % (', '.join(['"%s": %s' % (key, str(obj[key])) for key in obj]), )
    actual = serialize_by_field_to_json(obj)
    
    self.assertEqual(expected, actual)
  
  def test_simple_message(self):
    message = 'thing'
    rm = ResponseMessage(message)
    
    expected = '{"message": "%s"}' % (message, )
    actual = serialize_by_field_to_json(rm)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference(self):
    expected = \
      '{' \
        '"name": "recursive_test_1.", ' \
        '"public_data": ' \
        '[' \
          '{' \
            '"thing1": "%3Ccircular+reference%3E", ' \
            '"thing2": ' \
            '{' \
              '"name": "recursive_test_2.", ' \
              '"public_data": ' \
              '[' \
                '"%21", ' \
                '"%3Ccircular+reference%3E"' \
              ']' \
            '}' \
          '}' \
        ']' \
      '}'
    actual = serialize_by_field_to_json(recursively_joined_object_1, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_two_references_without_base_field_excluding_circular_references(self):
    expected = \
    '{' \
      '"name": "%s", ' \
      '"public_data": ' \
      '{' \
        '"name": "%s", ' \
        '"public_data": "%s", ' \
        '"private_data": "%s"' \
      '}, ' \
      '"private_data": ' \
      '{' \
        '"name": "%s", ' \
        '"public_data": "%s", ' \
        '"private_data": "%s"'\
      '}' \
    '}' % \
      (
        quote_plus(two_same_level_references.name),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data)
      )
    actual = serialize_by_field_to_json(two_same_level_references, public_only=False, skip_circular_references=True)
    
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
  
  def test_object_with_list_of_primitives(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '<Dummy><name>%s</name><public_data>%s</public_data></Dummy>' % (name, ''.join(['<item>' + item + '</item>' for item in public]))
    actual = serialize_by_field_to_xml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list_of_objects(self):
    name = 'dummy.'
    public = [Dummy('a', 'pub_a', None), Dummy('b', 'pub_b', None), Dummy('c', 'pub_c', None), Dummy('d', 'pub_d', None)]
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '<Dummy><name>%s</name><public_data>' \
               '<item><Dummy><name>a</name><public_data>pub_a</public_data></Dummy></item>' \
               '<item><Dummy><name>b</name><public_data>pub_b</public_data></Dummy></item>' \
               '<item><Dummy><name>c</name><public_data>pub_c</public_data></Dummy></item>' \
               '<item><Dummy><name>d</name><public_data>pub_d</public_data></Dummy></item>' \
               '</public_data></Dummy>'% (name,)
    actual = serialize_by_field_to_xml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_tuple(self):
    name = 'dummy.'
    public = ('a', 'b', 'c', 'd')
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = '<Dummy><name>%s</name><public_data><item>a</item><item>b</item><item>c</item><item>d</item></public_data></Dummy>' % (name, )
    actual = serialize_by_field_to_xml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_dict_of_primitives(self):
    obj = {'a': 1, 'b': 2, 'c': 3}
  
    expected = ''.join(['<%s>%s</%s>' % (key, str(obj[key]), key) for key in obj])
    actual = serialize_by_field_to_xml(obj)
  
    self.assertEqual(expected, actual)
  
  def test_simple_message(self):
    message = 'thing'
    rm = ResponseMessage(message)
    
    expected = '<message>%s</message>' % (message, )
    actual = serialize_by_field_to_xml(rm)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference(self):
    expected = '<Dummy>' \
                 '<name>recursive_test_1.</name>' \
                 '<public_data>' \
                   '<item>' \
                     '<Joiner>' \
                       '<thing1>%3Ccircular+reference%3E</thing1>' \
                       '<thing2>' \
                         '<Dummy>' \
                           '<name>recursive_test_2.</name>' \
                           '<public_data>' \
                             '<item>%21</item>' \
                             '<item>%3Ccircular+reference%3E</item>' \
                           '</public_data>' \
                         '</Dummy>' \
                       '</thing2>' \
                     '</Joiner>' \
                   '</item>' \
                '</public_data>' \
              '</Dummy>'
    actual = serialize_by_field_to_xml(recursively_joined_object_1, use_base_field=True, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference_without_base_field(self):
    expected = '<name>recursive_test_1.</name>' \
               '<public_data>' \
                 '<item>' \
                   '<thing1>%3Ccircular+reference%3E</thing1>' \
                   '<thing2>' \
                     '<name>recursive_test_2.</name>' \
                     '<public_data>' \
                       '<item>%21</item>' \
                       '<item>%3Ccircular+reference%3E</item>' \
                     '</public_data>' \
                   '</thing2>' \
                 '</item>' \
               '</public_data>'
    actual = serialize_by_field_to_xml(recursively_joined_object_1, use_base_field=False, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference_without_base_field_excluding_circular_references(self):
    expected = '<name>recursive_test_1.</name>' \
               '<public_data>' \
                 '<item>' \
                   '<thing2>' \
                     '<name>recursive_test_2.</name>' \
                     '<public_data>' \
                       '<item>%21</item>' \
                     '</public_data>' \
                   '</thing2>' \
                 '</item>' \
               '</public_data>'
    actual = serialize_by_field_to_xml(recursively_joined_object_1, use_base_field=False, skip_circular_references=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_two_references_without_base_field_excluding_circular_references(self):
    expected = '<name>%s</name>' \
               '<public_data>' \
                 '<name>%s</name>' \
                 '<public_data>%s</public_data>' \
                 '<private_data>%s</private_data>' \
               '</public_data>' \
               '<private_data>' \
                 '<name>%s</name>' \
                 '<public_data>%s</public_data>' \
                 '<private_data>%s</private_data>' \
               '</private_data>' % \
      (
        quote_plus(two_same_level_references.name),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data)
      )
    actual = serialize_by_field_to_xml(two_same_level_references, public_only=False, use_base_field=False, skip_circular_references=True)
    
    self.assertEqual(expected, actual)

class SerToYAMLTests(unittest.TestCase):
  def test_primitive(self):
    value = 2
    
    expected = '2'
    actual   = serialize_by_field_to_yaml(value)
    
    self.assertEqual(expected, actual)

  def test_empty_list(self):
    obj = []
  
    expected = ''
    actual = serialize_by_field_to_yaml(obj)
  
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
  
  def test_object_with_list_of_primitives(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data:\n    - "a"\n    - "b"\n    - "c"\n    - "d"' % (name, )
    actual = serialize_by_field_to_yaml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list_of_objects(self):
    name = 'dummy.'
    public = [Dummy('a', 'pub_a', None), Dummy('b', 'pub_b', None), Dummy('c', 'pub_c', None), Dummy('d', 'pub_d', None)]
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data:\n'\
               '    - Dummy:\n        name: "a"\n        public_data: "pub_a"\n' \
               '    - Dummy:\n        name: "b"\n        public_data: "pub_b"\n'\
               '    - Dummy:\n        name: "c"\n        public_data: "pub_c"\n'\
               '    - Dummy:\n        name: "d"\n        public_data: "pub_d"' % (name, )
    actual = serialize_by_field_to_yaml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_tuple(self):
    name = 'dummy.'
    public = ('a', 'b', 'c', 'd')
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data:\n    - "a"\n    - "b"\n    - "c"\n    - "d"' % (name, )
    actual = serialize_by_field_to_yaml(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_dict_of_primitives(self):
    obj = {'a': 1, 'b': 2, 'c': 3}
    
    expected = '\n'.join(['%s: %s' % (key, str(obj[key])) for key in obj])
    actual = serialize_by_field_to_yaml(obj)
    
    self.assertEqual(expected, actual)
  
  def test_simple_message(self):
    message = 'thing'
    rm = ResponseMessage(message)
    
    expected = 'message: "%s"' % (message, )
    actual = serialize_by_field_to_yaml(rm)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_object(self):
    child_name = 'child.'
    child = Dummy(child_name, None, None)
    
    parent_name = 'parent.'
    parent = Dummy(parent_name, child, None)
    
    expected = """Dummy:
  name: "%s"
  public_data:
    Dummy:
      name: "%s"
      public_data: null""" % (parent_name, child_name)
    actual = serialize_by_field_to_yaml(parent, use_base_field=True, skip_null_values=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference(self):
    expected = """Dummy:
  name: "recursive_test_1."
  public_data:
    - Joiner:
        thing1: "%3Ccircular+reference%3E"
        thing2:
          Dummy:
            name: "recursive_test_2."
            public_data:
              - "%21"
              - "%3Ccircular+reference%3E\""""
    actual = serialize_by_field_to_yaml(recursively_joined_object_1, use_base_field=True, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference_without_base_field(self):
    expected = """name: "recursive_test_1."
public_data:
  - thing1: "%3Ccircular+reference%3E"
    thing2:
      name: "recursive_test_2."
      public_data:
        - "%21"
        - "%3Ccircular+reference%3E\""""
    actual = serialize_by_field_to_yaml(recursively_joined_object_1, use_base_field=False, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference_without_base_field_excluding_circular_references(self):
    expected = """name: "recursive_test_1."
public_data:
  - thing2:
      name: "recursive_test_2."
      public_data:
        - "%21\""""
    actual = serialize_by_field_to_yaml(recursively_joined_object_1, use_base_field=False, skip_circular_references=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_two_references_without_base_field_excluding_circular_references(self):
    expected = """name: "%s"
public_data:
  name: "%s"
  public_data: "%s"
  private_data: "%s"
private_data:
  name: "%s"
  public_data: "%s"
  private_data: "%s\"""" % (
        quote_plus(two_same_level_references.name),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data)
      )
    actual = serialize_by_field_to_yaml(two_same_level_references, public_only=False, use_base_field=False, skip_circular_references=True)
    
    self.assertEqual(expected, actual)

class SerToTextTests(unittest.TestCase):
  def test_primitive(self):
    value = 2
    
    expected = '2'
    actual   = serialize_by_field_to_plain_text(value)
    
    self.assertEqual(expected, actual)
  
  def test_empty_list(self):
    obj = []
    
    expected = '(list)\n[\n]'
    actual = serialize_by_field_to_plain_text(obj)
    
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
  
  def test_object_with_list_of_primitives(self):
    name = 'dummy.'
    public = ['a', 'b', 'c', 'd']
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: (list)\n  [\n    %s\n  ]' % (name, '\n    '.join(['"%s",' % (item, ) for item in public])[:-1])
    actual = serialize_by_field_to_plain_text(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_list_of_objects(self):
    name = 'dummy.'
    public = [Dummy('a', 'pub_a', None), Dummy('b', 'pub_b', None), Dummy('c', 'pub_c', None), Dummy('d', 'pub_d', None)]
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: (list)\n  [\n'\
               '    Dummy:\n      name: "a"\n      public_data: "pub_a",\n' \
               '    Dummy:\n      name: "b"\n      public_data: "pub_b",\n'\
               '    Dummy:\n      name: "c"\n      public_data: "pub_c",\n'\
               '    Dummy:\n      name: "d"\n      public_data: "pub_d"\n' \
               '  ]' % (name, )
    actual = serialize_by_field_to_plain_text(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_tuple(self):
    name = 'dummy.'
    public = ('a', 'b', 'c', 'd')
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: (tuple)\n  (\n    "%s"\n  )' \
               % (name, '",\n    "'.join(str(item) for item in public))
    actual = serialize_by_field_to_plain_text(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_dict(self):
    name = 'dummy.'
    public = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    private = 'jkl;'
    value = Dummy(name, public, private)
    
    expected = 'Dummy:\n  name: "%s"\n  public_data: (dict)\n  {\n    %s\n  }' \
               % (name, ',\n    '.join('"%s": %s' % (str(key), str(public[key])) for key in public))
    actual = serialize_by_field_to_plain_text(value, use_base_field=True)
    
    self.assertEqual(expected, actual)
  
  def test_dict_of_primitives(self):
    obj = {'a': 1, 'b': 2, 'c': 3}
    
    expected = '(dict)\n{\n  %s\n}' % (',\n  '.join(['"%s": %s' % (key, str(obj[key])) for key in obj]), )
    actual = serialize_by_field_to_plain_text(obj)
    
    self.assertEqual(expected, actual)
  
  def test_simple_message(self):
    message = 'thing'
    rm = ResponseMessage(message)
    
    expected = 'message: "%s"' % (message, )
    actual = serialize_by_field_to_plain_text(rm, use_base_field=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_object(self):
    child_name = 'child.'
    child = Dummy(child_name, None, None)
    
    parent_name = 'parent.'
    parent = Dummy(parent_name, child, None)
    
    expected = """Dummy:
  name: "%s"
  public_data:
    Dummy:
      name: "%s"
      public_data: null""" % (parent_name, child_name)
    actual = serialize_by_field_to_plain_text(parent, skip_null_values=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference(self):
    expected = """Dummy:
  name: "recursive_test_1."
  public_data: (list)
  [
    Joiner:
      thing1: %3Ccircular+reference%3E
      thing2:
        Dummy:
          name: "recursive_test_2."
          public_data: (list)
          [
            "%21",
            %3Ccircular+reference%3E
          ]
  ]"""
    actual = serialize_by_field_to_plain_text(recursively_joined_object_1, use_base_field=True, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference_without_base_field(self):
    expected = """name: "recursive_test_1."
public_data: (list)
[
  thing1: %3Ccircular+reference%3E
  thing2:
    name: "recursive_test_2."
    public_data: (list)
    [
      "%21",
      %3Ccircular+reference%3E
    ]
]"""
    actual = serialize_by_field_to_plain_text(recursively_joined_object_1, use_base_field=False, skip_circular_references=False)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_recursive_reference_without_base_field_excluding_circular_references(self):
    expected = """name: "recursive_test_1."
public_data: (list)
[
  thing2:
    name: "recursive_test_2."
    public_data: (list)
    [
      "%21"
    ]
]"""
    actual = serialize_by_field_to_plain_text(recursively_joined_object_1, use_base_field=False, skip_circular_references=True)
    
    self.assertEqual(expected, actual)
  
  def test_object_with_two_references_without_base_field_excluding_circular_references(self):
    expected = """name: "%s"
public_data:
  name: "%s"
  public_data: "%s"
  private_data: "%s"
private_data:
  name: "%s"
  public_data: "%s"
  private_data: "%s\"""" % (
        quote_plus(two_same_level_references.name),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data),
        quote_plus(primitive_dummy.name), quote_plus(primitive_dummy.public_data), quote_plus(primitive_dummy._private_data)
      )
    actual = serialize_by_field_to_plain_text(two_same_level_references, public_only=False, use_base_field=False, skip_circular_references=True)
    
    self.assertEqual(expected, actual)

class GetQueryParamTests(unittest.TestCase):
  def test_get_default_values(self):
    query_params = {'catalog_id': '1'}
    
    self.assertEqual(False, GetSongsQueryParams.SONG_TITLE_HAS_WILDCARDS.default_value)
  
  def test_album_name_is_case_sensitive(self):
    query_params =\
    {
      'catalog_id': '1',
      'album_name': 'unit test',
      'album_name_is_case_sensitive': 'False',
      'album_name_matches_diacritics': 'True'
    }
    
    self.assertTrue(GetSongsQueryParams.ALBUM_NAME_IS_CASE_SENSITIVE.param_name in query_params)
    self.assertFalse(GetSongsQueryParams.ALBUM_NAME_IS_CASE_SENSITIVE.get_value(query_params, False)[0])

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

class TestCols(OrderColName):
  A = 'a', '1'
  B = 'b', '2'
  C = 'c', '3'

test_cols_by_name = { col.column_name: col for col in TestCols }

class OrderTests(unittest.TestCase):
  def test_build_order_by_clause(self):
    order_by = \
      [
        OrderByCol(TestCols.A, OrderDirection.ASCENDING),
        OrderByCol(TestCols.B, OrderDirection.DESCENDING),
        OrderByCol(TestCols.C, OrderDirection.ASCENDING)
      ]
    
    expected = ', '.join(ob.col.column_name + ' ' + ob.direction.value for ob in order_by)
    actual = get_order_clause(order_by)
    
    self.assertEqual(expected, actual)
  
  def test_parse_order_bys(self):
    query_param = 'a asc, b desc, c'
    parse_func = get_order_parser(TestCols, test_cols_by_name)
    
    expected = \
    [
      OrderByCol(TestCols.A, OrderDirection.ASCENDING),
      OrderByCol(TestCols.B, OrderDirection.DESCENDING),
      OrderByCol(TestCols.C, OrderDirection.ASCENDING),
    ]
    actual = parse_func(query_param)
    
    self.assertEqual(expected, actual)
  
  def test_parse_order_bys_with_full_directions(self):
    query_param = 'a, b descending, c ascending'
    parse_func = get_order_parser(TestCols, test_cols_by_name)
    
    expected = \
    [
      OrderByCol(TestCols.A, OrderDirection.ASCENDING),
      OrderByCol(TestCols.B, OrderDirection.DESCENDING),
      OrderByCol(TestCols.C, OrderDirection.ASCENDING),
    ]
    actual = parse_func(query_param)
    
    self.assertEqual(expected, actual)
  
  def test_parse_order_bys_with_invalid_column(self):
    bad_column = 'jkl'
    query_param = 'a, %s asc, c desc' % (bad_column, )
    parse_func = get_order_parser(TestCols, test_cols_by_name)
    
    found_error = False
    try:
      parse_func(query_param)
    except ValueError as e:
      found_error = True
      expected = '"%s" isn\'t a valid column name; valid column names are %s.' % (bad_column, ', '.join(col.column_name for col in TestCols))
      actual = str(e)
      self.assertEqual(expected, actual)
    
    self.assertTrue(found_error)
  
  def test_parse_order_bys_with_invalid_direction(self):
    bad_direction = 'jkl;'
    query_param = 'a, b %s, c jkl;' % (bad_direction, )
    parse_func = get_order_parser(TestCols, test_cols_by_name)
    
    found_error = False
    try:
      parse_func(query_param)
    except ValueError as e:
      found_error = True
      expected = 'the value "%s" can\'t be parsed as an order direction.' % bad_direction
      actual = str(e)
      self.assertEqual(expected, actual)
    
    self.assertTrue(found_error)

if __name__ == '__main__':
  unittest.main()