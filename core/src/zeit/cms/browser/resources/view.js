zeit.cms.View = gocept.Class.extend({

    construct: function(url, target_id, get_query_string) {
        var self = this;
        self.url = url;
        self.target_id = target_id
        self.get_query_string = get_query_string;
    },

    render: function(target_element, url) {
        var self = this;
        if (isUndefinedOrNull(url)) {
            url = self.url;
        }

        if (!isUndefinedOrNull(self.get_query_string)) {
            url += "?" + self.get_query_string();
        }

        self.load(target_element, url);
    },

    load: function(target_element, url) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX have to wrap in function to retain reference to self
        // otherwise this gets messed up
        d.addCallback(function(result) {
            self.do_render(result.responseText, target_element) });
        d.addErrback(zeit.cms.log_error);
    },

    do_render: function(html, target_element, data) {
        var self = this;
        var target_element = target_element || $(self.target_id);
        MochiKit.Signal.signal(self, 'before-load');
        target_element.innerHTML = html;
        log('template expanded successfully');
        MochiKit.Signal.signal(self, 'load', target_element, data);
    },
});


// need control over which URL is loaded (pass to class)
// how to retrieve which URL to load? often we'd get it from the JSON
// somehow. But how do we access the JSON? Through the template?
// need control over query string (pass to class)
// need control over which element is expanded (optionally pass to render)

zeit.cms.JSONView = zeit.cms.View.extend({

    load: function(target_element, url) {
        var self = this;
        var d = MochiKit.Async.loadJSONDoc(url);
        // XXX have to wrap in function to retain reference to self
        // otherwise this gets messed up
        d.addCallback(function(json) { self.callback_json(json, target_element) });
        d.addErrback(zeit.cms.log_error);
    },

    callback_json: function(json, target_element) {
        var self = this;
        var template_url = json['template_url'];
        if (template_url == self.last_template_url && 
            !isUndefinedOrNull(self.template)) {
            self.expand_template(json, target_element);
            return;
        }
        self.load_template(template_url, json, target_element);
    },

    load_template: function(template_url, json, target_element) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
        d.addCallback(function(result) {
            self.template = jsontemplate.Template(result.responseText, 
                                                  {default_formatter: 'html',
                                                   hooks: jsontemplate.HtmlIdHooks()});
            self.last_template_url = template_url;
            self.expand_template(json, target_element);
        });
        d.addErrback(zeit.cms.log_error);
        return d;
    },

    expand_template: function(json, target_element) {
        var self = this;
        self.do_render(self.template.expand(json), target_element, json);
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
    console.trace();
    console.error(real_error.name + ': ' + real_error.message);
};


(function() {

    zeit.cms.url_handlers = new MochiKit.Base.AdapterRegistry();

    var click_handler = function(event) {
        try {
            zeit.cms.url_handlers.match(event.target())
            event.preventDefault();
        } catch (e if e == MochiKit.Base.NotFound) {
        }
    };
    MochiKit.Signal.connect(window, 'onclick', click_handler);


})();
