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


(function() {

    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        zeit.find.tabs = new zeit.find.Tabs();
    });
})();


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
  MochiKit.Signal.signal(id, 'before-template-expand')
  $(id).innerHTML = s;
  log('template expanded successfully');
  if (!isUndefinedOrNull(init)) {
      init();
      log('initialization successful');
  }
  MochiKit.Signal.signal(id, 'after-template-expand')
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
    if ($('extended_search')) {
        $('extended_search_form').innerHTML = '';
    } else {
        var d = MochiKit.Async.loadJSONDoc(application_url + '/extended_search_form');
        d.addCallback(json_callback, 'extended_search_form');
        d.addErrback(log_error);
    }
  });
  MochiKit.Signal.connect('result_filters_button', 'onclick', function(e) {
    if ($('filter_Zeit')) {
        $('result_filters').innerHTML = '';
    } else {
        var d = MochiKit.Async.loadJSONDoc(application_url + '/result_filters');
        d.addCallback(json_callback, 'result_filters');
        d.addErrback(log_error);
    }
  });
};

var init = function() {
    var tab = new zeit.find.Tab('search_form', 'Suche');
    zeit.find.tabs.add(tab);
    var d = MochiKit.Async.loadJSONDoc(application_url + '/search_form');
    d.addCallback(json_callback, 'search_form', init_search_form);
    d.addErrback(log_error);
};

MochiKit.Signal.connect(window, 'onload', init);

})();


(function() {
    
    var draggables = [];

    var connect_draggables = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('search_result'));
        forEach(results, function(result) {
            draggables.push(new MochiKit.DragAndDrop.Draggable(result, {
                starteffect: null,
                endeffect: null}));
        });
    }

    var disconnect_draggables = function() {
        while(draggables.length > 0) {
            draggables.pop().destroy();
        }
    }

    var init = function() {
        var ident = MochiKit.Signal.connect(
            'search_form', 'after-template-expand', function() {
            MochiKit.Signal.disconnect(ident);
            MochiKit.Signal.connect(
                'search_result', 'before-template-expand', disconnect_draggables);
            MochiKit.Signal.connect(
                'search_result', 'after-template-expand', connect_draggables);
            });
    }

    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        init();
    });
})();



// Register empty tabs


(function() {
    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        zeit.find.tabs.add(new zeit.find.Tab('favorites', 'Favoriten'));
    });
})();


(function() {
    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        zeit.find.tabs.add(new zeit.find.Tab('for-this-page', 'Für diese Seite'));
    });
})();
