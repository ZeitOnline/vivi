zeit.cms.View = gocept.Class.extend({

    construct: function(url, target_id, get_query_string) {
        var self = this;
        self.url = url;
        self.target_id = target_id
        self.get_query_string = get_query_string;
    },

    render: function(target_element, url, query_string) {
        var self = this;
        if (isUndefinedOrNull(url)) {
            url = self.url;
        }
        if (isUndefinedOrNull(query_string) &&
            !isUndefinedOrNull(self.get_query_string)) {
            query_string = self.get_query_string();
        }
        if (!isUndefinedOrNull(query_string)) {
            if (typeof query_string != "string") {
                query_string = MochiKit.Base.queryString(query_string);
            }
            url += "?" + query_string;
        }
        return self.load(target_element, url);
    },

    load: function(target_element, url) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        d.addCallback(function(result) {
            return self.do_render(result.responseText, target_element)
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
        return d;
    },

    do_render: function(html, target_element, data) {
        var self = this;
        var target_element = target_element || $(self.target_id);
        MochiKit.Signal.signal(self, 'before-load');
        target_element.innerHTML = html;
        log('template expanded successfully', self.target_id);
        MochiKit.Signal.signal(self, 'load', target_element, data);
        return data
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
        var target_element = target_element || $(self.target_id);
        if(!isNull(target_element)) {
            MochiKit.DOM.addElementClass(target_element, 'busy');
        }
        var d = MochiKit.Async.loadJSONDoc(url);
        d.addCallback(function(json) {
            return self.callback_json(json, target_element);
        });
        d.addErrback(function(err) {
            zeit.cms.log_error(err);
            return err
        });
        d.addBoth(function(result) {
            MochiKit.DOM.removeElementClass(target_element, 'busy');
            return result
        });
        return d;
    },

    callback_json: function(json, target_element) {
        var self = this;
        var template_url = json['template_url'];
        if (template_url == self.last_template_url && 
            !isUndefinedOrNull(self.template)) {
            self.expand_template(json, target_element);
            return json
        }
        return self.load_template(template_url, json, target_element);
    },

    load_template: function(template_url, json, target_element) {
        var self = this;
        log("loading template", template_url)
        var d = MochiKit.Async.doSimpleXMLHttpRequest(template_url);
        d.addCallback(function(result) {
            self.template = jsontemplate.Template(
                result.responseText, {
                default_formatter: 'html',
                hooks: jsontemplate.HtmlIdHooks()});
            self.last_template_url = template_url;
            self.expand_template(json, target_element);
            return json
        });
        d.addErrback(function(err) {
            zeit.cms.log_error(err);
            return err
        });
        return d;
    },

    expand_template: function(json, target_element) {
        var self = this;
        self.do_render(self.template.expand(json), target_element, json);
    },
});

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
