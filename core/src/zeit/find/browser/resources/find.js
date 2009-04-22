zeit.find = {};

zeit.find.Tabs = gocept.Class.extend({
    // Knows about all tabs

    construct: function() {
        log("initializing tabs");
        var self = this;
        self.container = $('cp-forms');
        var div = self.container.appendChild(
            DIV({'class': 'context-views'}))
        self.tabs = [];
        self.tabs_element = div.appendChild(UL());
        MochiKit.Signal.connect(
            self.tabs_element, 'onclick', self, self.switch_tab);
    },

    add: function(tab) {
        // Create a tab inside $('cp-forms')
        var self = this;
        tab.tab_element = self.tabs_element.appendChild(
            LI({},
                A({href: tab.id}, tab.title)))
        tab.container = self.container.appendChild(DIV({id: tab.id}));
        MochiKit.DOM.hideElement(tab.container);
        self.tabs.push(tab);
        if (self.tabs.length == 1) {
            self.activate(tab.id);
        }
    },

    switch_tab: function(event) {
        var self = this;
        var target = event.target();
        var id = target.getAttribute('href');
        self.activate(id);
        event.stop();
    },

    activate: function(id) {
        var self = this;
        forEach(self.tabs, function(tab) {
            if (tab.id == id) {
                MochiKit.DOM.showElement(tab.container);
                MochiKit.DOM.addElementClass(tab.tab_element, 'selected');
            } else {
                MochiKit.DOM.hideElement(tab.container);
                MochiKit.DOM.removeElementClass(tab.tab_element, 'selected');
            }
        });
    },
});

zeit.find.Tab = gocept.Class.extend({

    construct: function(id, title) {
        var self = this;
        self.id = id;
        self.title = title;
        self.selected = false;
    },

});

// need control over which URL is loaded (pass to class)
// how to retrieve which URL to load? often we'd get it from the JSON
// somehow. But how do we access the JSON? Through the template?
// need control over query string (pass to class)
// need control over which element is expanded (optionally pass to render)

zeit.find.View = gocept.Class.extend({
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
        d.addErrback(zeit.find.log_error);
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
        d.addErrback(zeit.find.log_error);
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


zeit.find.log_error = function(err) {
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

(function() {

    var init_search_form = function() {
        MochiKit.Signal.connect('search_button', 'onclick', function(e) {
            search_result.render();
        });
        MochiKit.Signal.connect('extended_search_button', 'onclick', function(e) {
            if ($('extended_search')) {
                $('extended_search_form').innerHTML = '';
            } else {
                extended_search_form.render();
            }
        });
        MochiKit.Signal.connect('result_filters_button', 'onclick', function(e) {
            if ($('filter_Zeit')) {
                $('result_filters').innerHTML = '';
            } else {
                result_filters.render();
            }
        });
    };
    
    var draggables = [];

    var connect_draggables = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('search_result'));
        forEach(results, function(result) {
            draggables.push(zeit.cms.createDraggableContentObject(result));
        });
    }

    var connect_related = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('search_result'));
        forEach(results, function(entry) {
            var related_url = MochiKit.DOM.scrapeText(
                MochiKit.Selector.findChildElements(
                    entry, ['.related_url'])[0]);
            var related_links = MochiKit.Selector.findChildElements(
                entry, ['.related_links'])[0];
            var related_info = MochiKit.Selector.findChildElements(
                entry, ['.related_info'])[0];
            MochiKit.Signal.connect(related_links, 'onclick', function(e) {
                if (MochiKit.Selector.findChildElements(related_info,
                                                        ['.related_entry']).length > 0) {
                    MochiKit.DOM.removeElementClass(related_links, 'expanded');
                    related_info.innerHTML = '';
                } else {
                    MochiKit.DOM.addElementClass(related_links, 'expanded');
                    expanded_search_result.render(related_info, related_url);
                }
            });
        });
    }

    var disconnect_draggables = function() {
        while(draggables.length > 0) {
            draggables.pop().destroy();
        }
    }
   
    var init = function() {
        zeit.find.tabs = new zeit.find.Tabs();
        zeit.find.tabs.add(new zeit.find.Tab('search_form', 'Suche'));
        zeit.find.tabs.add(new zeit.find.Tab('favorites', 'Favoriten'));
        zeit.find.tabs.add(new zeit.find.Tab('for-this-page', 'Für diese Seite'));
        search_form.render();
    };
    
    search_form = new zeit.find.View(
        'search_form', 'search_form');
    search_result = new zeit.find.View(
        'search_result', 'search_result', 
        function() {
            return 'fulltext=' + $('fulltext').value;
        });
    extended_search_form = new zeit.find.View(
        'extended_search_form', 'extended_search_form');
    result_filters = new zeit.find.View(
        'result_filters', 'result_filters')
    expanded_search_result = new zeit.find.View(
        'expanded_search_result')

    MochiKit.Signal.connect(window, 'onload', init);
    MochiKit.Signal.connect(search_form, 'load', init_search_form);
    MochiKit.Signal.connect(search_result, 'before-load', 
                            disconnect_draggables);
    MochiKit.Signal.connect(search_result, 'load', 
                            connect_related);
    MochiKit.Signal.connect(search_result, 'load', 
                            connect_draggables);
     
})();
