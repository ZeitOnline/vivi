(function() {

var template_cache = {};

var load_template = function(template_url, json, id) {
  var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
  d.addCallback(function(result) {
    var t = jsontemplate.Template(result.responseText);
    template_cache[template_url] = t;
    expand_template(t, json, id);
  });
  d.addErrback(log_error);
  return d;
};

var expand_template = function(template, json, id) {
  var s = template.expand(json);
  $(id).innerHTML = s;
  log('template expanded successfully');
};

var json_callback = function(id, json) {
  var template_url = json['template_url'];
  var template = template_cache[template_url];
  if (!isUndefinedOrNull(template)) {
    expand_template(template, json, id);
    return;
  }
  load_template(template_url, json, id);
};

var log_error = function(err) {
    console.error(err.message.name + ': ' + err.message.message);
};

var find = function(url) {
  var d = MochiKit.Async.loadJSONDoc(url);
  d.addCallback(json_callback, 'search_result');
  d.addErrback(log_error);
};

var init = function() {
  MochiKit.Signal.connect('search_button', 'onclick', function(e) {
    var find_url = 'find?fulltext=' + $('fulltext').value;
    find(find_url);
  });
};

MochiKit.Signal.connect(window, 'onload', init);

})();
