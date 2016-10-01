function chk_empty(type)
{
  var txt = document.getElementById(type + '_txt');
  var chk = document.getElementById('no_' + type + '_chk');
  var btn = document.getElementById(type + '_btn');
  
  txt.disabled = !txt.disabled;
  btn.disabled =  txt.disabled;
  if (txt.disabled)
  {
    chk.innerHTML = 'Y';
    chk.className = "toxic_green";
  }
  else
  {
    chk.innerHTML = 'N';
    chk.className = "toxic_brown";
  }
}

function filter(type)
{
  var filters = '';
  var types   = ['song', 'artist', 'album', 'genre'];
  
  for (x in types)
  {
    var txt = document.getElementById(types[x] + '_txt');
    if (txt.disabled)
    {
      filters += '&' + types[x] + '_name=';
    }
    else if (txt.value.length > 0)
    {
      var filter = txt.value;
      filter     = filter.replace(/&/g, '%26');
      filters += '&' + types[x] + '_name=' + filter;
    }
  }
  
  load_view('browse', 'browse', 'what=' + type + 's' + filters, document.getElementById('browse_' + type + 's_list_div'), function() {}, true);
}