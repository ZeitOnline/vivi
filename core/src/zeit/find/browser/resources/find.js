(function() {

var template_cache = {};

var load_template = function(template_url, json, id) {
  var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
  d.addCallback(function(result) {
    t = make_template(template_url, result.responseText);
    expand_template(t, json, id);
  });
  return d;
};

var make_template = function(template_url, template_source) {
  var t = jsontemplate.Template(template_source);
  template_cache[template_url] = t;
  return t;
};

var expand_template = function(template, json, id) {
  var s = t.expand(json);
  $(id).innerHTML = s;
};

var json_callback = function(json) {
  var id = 'search_result';
  var template_url = json['template_url'];
  var template = template_cache[template_url];
  if (!isUndefinedOrNull(template)) {
    expand_template(template, json, id);
    return;
  }
  load_template(template_url, json, id);
};

var json_errback = function(error) {
  log('error when getting find json');
};

var render = function() {
  var d = MochiKit.Async.loadJSONDoc('find');
  d.addCallbacks(json_callback, json_errback);
};

MochiKit.Signal.connect(window, 'onload', render);

})();
