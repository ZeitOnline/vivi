(function() {

var json_callback = function(result) {
    log('success');
    /*
    var template_url = json['template_url'];
    var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
    d.addCallback(function(result) {
      var t = jsontemplate.JSONTemplate(result.responseText);
      var s = t.expand(json);
      $('search_result').innerHTML = s;
    });
    return d;
    */
};

var json_errback = function(error) {
    log('error');
}

var render = function() {
  log('enter render');
  var d = MochiKit.Async.doSimpleXMLHttpRequest('find');
  log('render I');
  d.addCallbacks(json_callback, json_errback);
  log('render II');
};

//MochiKit.Signal.connect(window, 'onload', render);
render();

})();
