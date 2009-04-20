(function() {

var json_callback = function(json) {
    var template_url = json['template_url'];
    var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
    d.addCallback(function(result) {
      var t = jsontemplate.Template(result.responseText);
      var s = t.expand(json);
      $('search_result').innerHTML = s;
    });
    return d;
};

var json_errback = function(error) {
    log('error when getting find json');
}

var render = function() {
  var d = MochiKit.Async.loadJSONDoc('find');
  d.addCallbacks(json_callback, json_errback);
};

MochiKit.Signal.connect(window, 'onload', render);

})();
