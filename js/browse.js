function show_hide_browse_lists(list_name)
{
  var lnk = document.getElementById('show_hide_' + list_name + '_lnk');
  var div = document.getElementById('browse_' + list_name + '_list_div');
  
  if (lnk == null)
  {
    alert('null lnk.');
    return;
  }
  
  if (div == null)
  {
    alret('null div.');
    return;
  }
  
  if (lnk.innerHTML.substring(0, 1) == '-')
  {
    div.style.display = 'none';
    lnk.innerHTML     = '+' + lnk.innerHTML.substring(1, lnk.innerHTML.length);
  }
  else
  {
    div.style.display = 'block';
    lnk.innerHTML     = '-' + lnk.innerHTML.substring(1, lnk.innerHTML.length);
  }
}

function filter_by(type, val, val_type)
{
  if (val_type != 'id' && val_type != 'name')
  {
    alert('invalid value type: "' + val_type + '"');
    return;
  }
  
  var types      = ['artist', 'album', 'genre', 'song'];
  var param_name = type + '_' + val_type;
  
  for (var i = 0; i < types.length; ++i)
  {
    if (type === types[i])
      continue;
    
    var view_div       = document.getElementById('browse_' + types[i] + 's_list_div');
    var old_params_div = document.getElementById('browsing_' + types[i] + 's_get_my_parent');
    
    if (view_div == null || view_div == undefined || old_params_div == null || old_params_div == undefined)
      continue;
    
    var old_params = old_params_div.innerHTML;
    var new_val    = val;
    
    while (old_params.indexOf('&amp;') >= 0)
      old_params = old_params.replace('&amp;', '&');
    
    old_params = remove_query_param(old_params, 'page');
    old_params = remove_query_param(old_params, 'view');
    
    if (val_type == 'id')
    {
      if (isNaN(parseInt(val)))
      {
        alert('invalid id: "' + val + '"');
        return;
      }
      
      var old_val = get_query_param_value(old_params, param_name);
      if (old_val != null)
      {
        var tmp     = old_val.split(',');
        var found   = false;
        var min     = 0;
        var max     = tmp.length - 1;
        var int_val = parseInt(val);
        var cur     = null;
        
        while (min <= max && !found)
        {
          cur         = parseInt((min + max)/2);
          var int_tmp = parseInt(tmp[cur]);
          
          if (int_tmp == int_val)
            found = true;
          else if (int_val > int_tmp)
            min = cur + 1;
          else // if (int_val < int_tmp)
            max = cur - 1;
        }
        
        new_val = (!found && parseInt(tmp[0]) > int_val ? val + ',' : '');
        
        if (cur < tmp.length && tmp[cur] < int_val)
          ++cur;
        
        tmp.splice(cur, 0, int_val);
        new_val = tmp.join(',');
        
      }
    }
    
    var new_params = set_query_param_value(old_params, param_name, new_val);
    new_params     = set_query_param_value(new_params, 'offset',   0);
    
    load_view('browse', 'browse', new_params, view_div, function() {}, true);
  }
}