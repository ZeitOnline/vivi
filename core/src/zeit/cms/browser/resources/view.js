
// need control over which URL is loaded (pass to class)
// how to retrieve which URL to load? often we'd get it from the JSON
// somehow. But how do we access the JSON? Through the template?
// need control over query string (pass to class)
// need control over which element is expanded (optionally pass to render)

zeit.cms.JSONView = gocept.Class.extend({
    construct: function(json_url, expansion_id, get_query_string) {
        var self = this;
        self.json_url = json_url;
        self.expansion_id = expansion_id
        self.get_query_string = get_query_string;
        self.template = null;
    },

    render: function(expansion_element, json_url) {
        var self = this;
        var url;
        if (isUndefinedOrNull(json_url)) {
            // XXX dependency on application_url...
            url = application_url + '/' + self.json_url;

        } else {
            url = application_url + '/' + json_url
        }

        if (!isUndefinedOrNull(self.get_query_string)) {
            url += "?" + self.get_query_string();
        }
        var d = MochiKit.Async.loadJSONDoc(url);
        // XXX have to wrap in function to retain reference to self
        // otherwise this gets messed up
        d.addCallback(function(json) { self.callback_json(json, expansion_element) });
        d.addErrback(zeit.cms.log_error);
    },

    callback_json: function(json, expansion_element) {
        var self = this;
        var template_url = json['template_url'];
        var template = self.template;
        if (!isUndefinedOrNull(template)) {
            self.expand_template(json, expansion_element);
            return;
        }
        self.load_template(template_url, json, expansion_element);
    },

    load_template: function(template_url, json, expansion_element) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
        d.addCallback(function(result) {
            var t = jsontemplate.Template(result.responseText);
            self.template = t;
            self.expand_template(json, expansion_element);
        });
        d.addErrback(zeit.cms.log_error);
        return d;
    },

    expand_template: function(json, expansion_element) {
        var self = this;
        var s = self.template.expand(json);
        var expansion_element = expansion_element || $(self.expansion_id);
        MochiKit.Signal.signal(self, 'before-load')
        expansion_element.innerHTML = s;
        log('template expanded successfully');
        MochiKit.Signal.signal(self, 'load')
    },
});

zeit.cms.log_error = function(err) {
    /* the error can be either a normal error or wrapped
       by MochiKit in a GenericError in which case the message
       is the real error. We check whether the message is the real
       error first by checking whether its information is undefined.
       If it is undefined, we fall back on the outer error and display
       information about that */
    var real_error = err.message;
    if (isUndefinedOrNull(real_error.message)) {
        real_error = err;
    }
    console.error(real_error.name + ': ' + real_error.message);
};
