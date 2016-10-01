function clear_txt(thing, txt)
{
  if (thing == null || thing.value != txt)
    return;
  
  thing.value = "";
}

function add_txt(thing, txt)
{
  if (thing == null || thing.value != "")
    return;
  
  thing.value = txt;
}

/**
 * @param query_str the query string to get the parameter value from
 * @param param_name the name of the parameter whose value to get
 * @return the string value associated with the given parameter name, or null if the parameter name wasn't found
 */
function get_query_param_value(query_str, param_name)
{
  var params = query_str.split('&');
  for (var i in params)
  {
    var param = params[i].split('=');
    if (param.length != 2)
      continue;
    
    if (param[0] === param_name)
      return param[1];
  }
  
  return null;
}

/**
 * @param orig_query_str the query string to modify
 * @param param_name the name of the parameter whose value to set or add
 * @param new_value the new value of the parameter in question
 * @return the modified query string.  (leaves the original in tact.)
 */
function set_query_param_value(orig_query_str, param_name, new_value, add_it)
{
  add_it = (typeof add_it === 'undefined' ? true : add_it);
  
  var params        = orig_query_str.split('&');
  var new_query_str = '';
  var found         = false;
  
  for (var x in params)
  {
    var param = params[x].split('=');
    if (param.length != 2) // invalid parameter; ignore it.
      continue;
    
    new_query_str += (param[0] + '=');
    if (param[0] == param_name)
    {
      new_query_str += new_value;
      found          = true;
    }
    else
    {
      new_query_str += param[1];
    }
    new_query_str += '&';
  }
  
  if (add_it && !found)
    new_query_str += (param_name + '=' + new_value + '&');
  
  new_query_str = new_query_str.substring(0, new_query_str.length - 1); // shave off the last &
  return new_query_str;
}

function remove_query_param(orig_query_str, param_name)
{
  var params        = orig_query_str.split('&');
  var new_query_str = '';
  var found         = false;
  
  for (var x in params)
  {
    var param = params[x].split('=');
    if (param.length != 2) // invalid parameter; ignore it.
      continue;
    
    if (param[0] != param_name)
      new_query_str += (param[0] + '=' + param[1] + '&');
  }
  
  if (new_query_str.length > 1)
    new_query_str = new_query_str.substr(0, new_query_str.length - 1);
  
  return new_query_str;
}

var key_sequence    = [];
var sequence_events = [];
function add_keystroke(event)
{
  key_sequence[key_sequence.length] = event.keyCode;
  var key = key_sequence;
  
  while (key.length > 0)
  {
    var should_break = false;
    var evts         = sequence_events;
    
    for (var i = 0; i < key.length; ++i)
    {
      if (Object.prototype.toString.call(evts[key[i]]) === "[object Array]")
      {
        evts = evts[key[i]];
      }
      else
      {
        if ((typeof evts[key[i]]) == 'function')
        {
          evts[key[i]]();
          key_sequence = [];
          should_break = true;
        }
        
        break;
      }
    }
    
    if (should_break)
      break;
    
    key.splice(0, 1);
  }
  
  if (key_sequence.length > 2)
    key_sequence = key_sequence.substring(1);
}

function load_index(event)
{
  load_view('now_playing', 'now_playing', '', document.getElementById('now_playing_div'), function() {}, true);
  
  // make / put focus on the search box
  window.strip_search_slash = false;
  sequence_events[191] = function()
  {
    var tag_name = document.activeElement.tagName.toLowerCase();
    if (tag_name === 'input')
      return;
    
    window.strip_search_slash = true;
    document.getElementById('search_txt').focus();
    
    // stupid extra /
    var fix_stuff = function()
    {
      document.getElementById('search_txt').value = '';
    };
    
    setTimeout(fix_stuff, 1);
  };
    
  // make esc put focus on the body
  sequence_events[27] = function()
  {
    document.activeElement.blur();
  };
}