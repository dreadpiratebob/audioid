var scanning = false;

function catalog_on_submit(index)
{
  var thing = document.getElementById('cat_' + index + '_cmd');
  if (thing == null)
    return false;
  
  var cmd = thing.value;
  
  if (cmd == 'update')
  {
    update_catalog(index);
    return false;
  }
  else if (cmd == 'delete')
  {
    return true;
  }
  else
  {
    alert('unknown command "' + cmd + '".');
    return false;
  }
}

function update_catalog(index)
{
  var thing = document.getElementById('catalog_id_' + index);
  if (thing == null)
    return;
  var id = thing.value;
  
  var thing = document.getElementById('catalog_name_' + index);
  if (thing == null)
    return;
  var name = thing.value;
  
  var thing = document.getElementById('catalog_path_' + index);
  if (thing == null)
    return;
  var path = thing.value;
  
  document.getElementById('scan_steps').innerHTML  = 'updating...<br />\n';
  document.getElementById('scan_steps').innerHTML += exec_cmd('catalog_editor', 'update', 'cat_id=' + id + '&name=' + name + '&path=' + path, true, null);
}

function load_scan_data(index)
{
  document.getElementById('scan_steps').innerHTML  = '';
  
  document.getElementById('scan_steps').innerHTML += 
    'add artist separators?<br />\n' +
    '<div id="cat_index" style="display: none;">' + index + '</div>' +
    '<div id="artist_separator_ct" style="display: none;">12</div>\n' +
    '<div id="artist_separator_div_0">\n' +
    '  <input type="text" value=" feat. " id="artist_separator_0" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(0); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" feat " id="artist_separator_1" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(1); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" Feat. " id="artist_separator_2" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(2); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" Feat " id="artist_separator_3" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(3); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" ft. " id="artist_separator_4" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(4); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" ft " id="artist_separator_5" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(5); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" vs. " id="artist_separator_6" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(6); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" vs " id="artist_separator_7" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(7); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" %26 " id="artist_separator_8" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(8); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=", " id="artist_separator_9" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(9); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" remixed by " id="artist_separator_10" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(10); return false;" style="text-decoration: none;">-</a><br />\n' +
    '  <input type="text" value=" covered by " id="artist_separator_11" />&nbsp;' +
      '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
      '<a href="#" onclick="remove_separator(11); return false;" style="text-decoration: none;">-</a><br />\n' +
    '</div>\n' +
    '<button type="button" id="artist_separator_end" onclick="scan_catalog(parseInt(document.getElementById(\'cat_index\').innerHTML));">scan it</button>';
}

function add_separator()
{
  var new_div         = document.createElement('div');
  var last_div        = document.getElementById('artist_separator_end');
  var index_div       = document.getElementById('artist_separator_ct');
  var index           = parseInt(index_div.innerHTML);
  
  index_div.innerHTML = (index + 1);
  new_div.id          = ('artist_separator_div_' + index);
  new_div.innerHTML   =
    '  <input type="text" value="" id="artist_separator_' + index + '" />&nbsp;' +
       '<a href="#" onclick="add_separator(); return false;" style="text-decoration: none;">+</a>&nbsp;' +
       '<a href="#" onclick="remove_separator(' + index + '); return false;" style="text-decoration: none;">-</a>';
  
  document.getElementById('scan_steps').insertBefore(new_div, last_div);
}

function remove_separator(index)
{
  var old_id    = 'artist_separator_div_' + index;
  var index_div = document.getElementById('artist_separator_ct');
  var max       = parseInt(index_div.innerHTML);
  var old_div   = document.getElementById(old_id);
  
  document.getElementById('scan_steps').removeChild(old_div);
  
  index_div.innerHTML = (max - 1);
  
  var tmp_div = document.getElementById('artist_separator_div_' + (index + 1));
  for(var i = index + 1; tmp_div !== null && tmp_div !== undefined; ++i)
  {
    tmp_div.id = 'artist_separator_div_' + (i - 1);
    tmp_div    = document.getElementById('artist_separator_div_' + (i + 1));
  }
}

function get_artist_separators()
{
  var separators = '';
  var some_txt   = document.getElementById('artist_separator_0');
  
  for (var i = 1; some_txt !== undefined && some_txt !== null; ++i)
  {
    separators += '|' + some_txt.value.replace(/&/g, '&');
    
    some_txt = document.getElementById('artist_separator_' + i);
  }
  separators = separators.substring(1);
  
  return separators;
}

function scan_catalog_old(index)
{
  if (scanning)
  {
    alert('already scanning. please wait.');
    return;
  }
  
  var thing = document.getElementById('catalog_id_' + index);
  if (thing == null)
    return;
  var id = thing.value;
  
  scanning = true;
  document.getElementById('scan_steps').innerHTML = 'scanning filenames...';
  
  var on_load_fn = function(feedback)
  {
    document.getElementById('scan_steps').innerHTML = 'done.';
    exec_cmd('catalog_editor', 'clear_scan_status', 'type=now', false, function(feedback){});
    scanning = false;
  };
  
  exec_cmd('catalog_editor', 'scan', 'id=' + id, false, on_load_fn)
  
  get_scan_status('.&nbsp;&nbsp;');
}

function scan_catalog(index)
{
  if (scanning)
  {
    alert('already scanning. please wait.');
    return;
  }
  
  var thing = document.getElementById('catalog_id_' + index);
  if (thing == null)
    return;
  var id = thing.value;
  
  scanning = true;
  
  var artist_separators = get_artist_separators();
  document.getElementById('scan_steps').innerHTML = 'scanning filenames...';
  
  var part1 = function(feedback)
  {
    exec_cmd('catalog_editor', 'load_mp3', 'id=' + id, false, part2, part2_err);
  };
  
  var part2 = function(feedback)
  {
    var last = feedback.substr(feedback.length - 4);
    if (last !== 'next')
    {
      exec_cmd('catalog_editor', 'clear_scan_status', 'type=now', false, part3);
      return;
    }
    
    exec_cmd('catalog_editor', 'load_mp3', 'id=' + id, false, part2, part2_err);
  }
  
  var part2_err = function(feedback, code)
  {
    part2('next');
  }
  
  var part3 = function(feedback)
  {
    document.getElementById('scan_steps').innerHTML = 'done.';
    scanning = false;
  };
  
  // exec_cmd('catalog_editor', 'load_filenames', 'id=' + id + '&separators=' + artist_separators, false, part1)
  
  exec_cmd('catalog_editor', 'scan', 'id=' + id + '&artist_separators=' + artist_separators)
  
  get_scan_status('.&nbsp;&nbsp;');
}

function get_scan_status(ending)
{
  var status = exec_cmd('catalog_editor', 'get_scan_status', 'max=40', true, null);
  document.getElementById('scan_feedback').innerHTML = status + '<br /><button type="button" onclick="var cmd=\'write_log\'; if (confirm(\'clear?\')) cmd=\'clear_scan_status\'; exec_cmd(\'catalog_editor\', cmd, \'nuke=false\', false, function (feedback) {});">write log</button>';
  var status_end = status.substring(status.length - 12, status.length);
  if (scanning && status_end != 'done.<br />\n')
  {
    document.getElementById('scan_feedback').innerHTML += ending;
    
    setTimeout
    (
      function()
      {
        var new_ending = null;
        
        if (ending == '.&nbsp;&nbsp;')
          new_ending = '&nbsp;.&nbsp;';
        else if (ending == '&nbsp;.&nbsp;')
          new_ending = '&nbsp;&nbsp;.';
        else
          new_ending = '.&nbsp;&nbsp;';
        
        get_scan_status(new_ending);
      },
      400
    );
  }
  else
  {
    scanning = false;
  }
}