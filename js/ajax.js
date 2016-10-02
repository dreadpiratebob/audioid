// send_request (at the bottom of this file) is probly the most (and only) useful function here.  there's a comment there that describes how to use it.

function get_value(_current, _default)
{
  if (_current == undefined || _current == null)
    return _default;
  
  return _current;
}

function _request_obj (rel_path, method, params, async, on_load_function, on_err_function)
{
  this.on_load_function = on_load_function;
  this.on_err_function  = on_err_function;
  this._xml_request     = new XMLHttpRequest();
  this.index            = _requests.length;
  var self = this;
  var base_url = "http://73.97.180.167/audioid/"; // This can be changed to the base dir for whatever project is using this file; rel_path will be relative to this.
  
  method = get_value(method, "GET").toUpperCase();
  async  = get_value(async,  false);
  
  this._xml_request.open(method, base_url + rel_path, async);
  this._xml_request.setRequestHeader("User-Agent",navigator.userAgent);
  
  if (method == "POST")
  {
    this._xml_request.setRequestHeader("Content-type",   "application/x-www-form-urlencoded");
    this._xml_request.setRequestHeader("Content-length", params.length);
  }
  
  if (typeof(this.on_load_function) != "function")
    this.on_load_function = function(feedback) {};
  
  if (typeof(this.on_err_function) != "function")
    this.on_err_function = function(feedback, error_num) { alert('error (' + error_num + '): ' + feedback); };
  
  if (async == true)
  {
    this._xml_request.onreadystatechange = function()
    {
      _requests[self.index] = null;
      if (self._xml_request.readyState == 4)
      {
        if (self._xml_request.status == 200)
          self.on_load_function(self._xml_request.responseText);
        else
          self.on_err_function(self._xml_request.responseText, self._xml_request.status);
      }
    }
  }

  this._xml_request.send(params);
}

var _requests = [];

/**
 * sends a request to base_path+rel_path (where base_path is defined above (see my comment), and is empty right now) and either returns the reponse or calls on_load_fn with the response
 * 
 * @param rel_path the path relative to base_path (as defined above)
 * @param method the request method ("GET" by default; can be "POST", "PUT" or "DELETE")
 * @param params query parameters to send with the request
 * @param async if true, this method won't return anything; instead it'll call on_load_fn with the response text as an argument.  if false, this method won't finish until the response has come back, at which point, it'll return the response text.
 * @param on_load_fn the function to call when the response comes back if async is true
 * 
 * @return nothing if async is true; the response text if async is false
 */
function send_request(rel_path, method, params, async, on_load_fn, on_err_fn)
{
  var _request = new _request_obj(rel_path, method, params, async, on_load_fn, on_err_fn);
  _requests[_requests.length] = _request;
  
  
  if (async === undefined || async === null || async === false)
    return _request._xml_request.responseText;
}

var _responses = [];
function _response(div, params, on_load_fn, on_err_fn)
{
  var self = this;
  
  if (on_load_fn === null || on_load_fn === undefined || (typeof on_load_fn) !== "function") // if no on_load function was passed in
    on_load_fn = function(_json) { /* do nothing here */ };
  
  if (on_err_fn === null || on_err_fn === undefined || (typeof on_err_fn) !== "function") // if no on_load function was passed in
    on_err_fn = function(_json) { /* do nothing here */ };
  
  this.div    = div;
  this.params = params;
  this.index  = _responses.length;
  
  this.on_load_fn  = on_load_fn;
  this.on_err_fn   = on_err_fn;
  this.response_fn = function(_json)
  {
    _responses[self.index] = null;
    
    if (_json.length == 0)
    {
      alert("error loading a vew; no data returned.");
      return;
    }
    
    if (_json.substr(0, 1) != "{")
    { // >:-|
      alert("the server returned an invalid view.\n" + _json);
      return;
    }
    
    var json = null;
    eval("json=" + _json);
    
    if (json.view == undefined || json.on_load == undefined)
    {
      self.div.innerHTML = "please <a href='log_in.php'>log back in</a>.  (you're probably seeing this because you left this page idle too long and then clicked a link.  the server here will log you out after a long enough period without any activity, and i haven't made the page refresh when it does that.)";
      return;
    }
    
    self.div.innerHTML = json.view;
    // according to the json standards on json.org, i'm not allowed to use a function as a value in json, so i have to put it in a quoted string and eval it.
    /* that's kinda stupid, though.
    var on_load = null;
    eval("on_load = " + json.on_load);
    on_load();
    /*/
    json.on_load();
    //*/
    
    self.on_load_fn(_json);
  };
  
  _responses[_responses.length] = this;
}

function load_view(page, view, params, div, on_load_fn, skip_login_check, smooth_load, on_err_fn)
{
  if (smooth_load !== true)
    smooth_load = false;
  
  var new_params = 
      "page=" + page +
      "&view=" + view;
  
  if (skip_login_check === true)
    new_params += "&skip_login_check=true";
  
  if (params.length > 0)
    new_params = new_params + "&" + params;
  
  if (div == null || div == undefined)
  {
    alert("null div.\npage: " + page + "\nview: " + view + "\nparams: " + params);
    return;
  }
  
  if (!smooth_load)
    div.innerHTML = "loading...";
  var response  = new _response(div, new_params, on_load_fn, on_err_fn);
  send_request("view.php", "POST", new_params, true, response.response_fn, response.on_err_fn);
}

function exec_cmd(page, cmd, params, return_feedback, on_load_fn, on_err_fn)
{
  if (params.length == 0)
    return;
  
  var new_params = 
        "page=" + page +
        "&cmd=" + cmd +
        "&" + params
  
  
  if (return_feedback == true)
  {
    var data = send_request("command.php", "POST", new_params, false, function(feedback) {}, on_err_fn);
    return data;
  }
  else
  {
    if ((typeof on_load_fn) !== "function")
      on_load_fn = function(feedback) {};
    
    send_request
    (
      "command.php",
      "POST",
      new_params,
      true,
      on_load_fn,
      on_err_fn
    );
  }
}
