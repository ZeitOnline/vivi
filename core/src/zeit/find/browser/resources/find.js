(function() {

var template_cache = {};

var load_template = function(template_url, json, id, init) {
  var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
  d.addCallback(function(result) {
    var t = jsontemplate.Template(result.responseText);
    template_cache[template_url] = t;
    expand_template(t, json, id, init);
  });
  d.addErrback(log_error);
  return d;
};

var expand_template = function(template, json, id, init) {
  var s = template.expand(json);
  $(id).innerHTML = s;
  log('template expanded successfully');
  if (!isUndefinedOrNull(init)) {
      init();
      log('initialization successful');
  }
};

var json_callback = function(id, init, json) {
  if (isUndefinedOrNull(json)) {
    // Allow the case, where init is not passed to this callback.
    json = init;
    init = null;
  }
  var template_url = json['template_url'];
  var template = template_cache[template_url];
  if (!isUndefinedOrNull(template)) {
    expand_template(template, json, id, init);
    return;
  }
  load_template(template_url, json, id, init);
};

var log_error = function(err) {
    console.error(err.name + ': ' + err.message);
};

var find = function(url) {
  var d = MochiKit.Async.loadJSONDoc(url);
  d.addCallback(json_callback, 'search_result');
  d.addErrback(log_error);
};

var init_search_form = function() {
  MochiKit.Signal.connect('search_button', 'onclick', function(e) {
    var search_result_url = application_url + '/search_result?fulltext=' + $('fulltext').value;
    find(search_result_url);
  });
  MochiKit.Signal.connect('extended_search_button', 'onclick', function(e) {
    var d = MochiKit.Async.loadJSONDoc(application_url + '/extended_search_form');
    d.addCallback(json_callback, 'extended_search_form');
    d.addErrback(log_error);
  });
};

var init = function() {
  var d = MochiKit.Async.loadJSONDoc(application_url + '/search_form');
  d.addCallback(json_callback, 'search_form', init_search_form);
  d.addErrback(log_error);
};

MochiKit.Signal.connect(window, 'onload', init);

})();
