zeit.cms.all_tabs = {}

zeit.cms.Tabs = gocept.Class.extend({
    // Knows about all tabs

    construct: function(container) {
        log("initializing tabs");
        var self = this;
        self.container = $(container);
        var div = self.container.appendChild(
            DIV({'class': 'context-views'}))
        self.tabs = [];
        self.tabs_element = div.appendChild(UL());
        MochiKit.Signal.connect(
            self.tabs_element, 'onclick', self, self.switch_tab);
    },

    add: function(tab) {
        var self = this;
        tab.after_add(self);
        self.tabs.push(tab);
        if (self.tabs.length == 1) {
            tab.activate();
        }
        zeit.cms.all_tabs[tab.id] = tab;
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
                tab.activate();
                self.active_tab = tab;
            } else {
                tab.deactivate();
            }
        });
        var parent_tab = zeit.cms.all_tabs[self.container.id];
        if (!isUndefinedOrNull(parent_tab)) {
            parent_tab.tabs.activate(self.container.id);
        }
    },

});

zeit.cms.Tab = gocept.Class.extend({

    construct: function(id, title) {
        var self = this;
        self.id = id;
        self.title = title;
    },

    after_add: function(parent) {
        var self = this;
        self.tabs = parent;
        self.tab_element = self.tabs.tabs_element.appendChild(
            LI({},
                A({href: self.id}, self.title)))
        self.container = self.tabs.container.appendChild(
            DIV({id: self.id, 'class': 'tab-content'}));
        self.deactivate();
    },

    activate: function() {
        var self = this;
        MochiKit.DOM.showElement(self.container);
        MochiKit.DOM.addElementClass(self.tab_element, 'selected');
    },

    deactivate: function() {
        var self = this;
        MochiKit.DOM.hideElement(self.container);
        MochiKit.DOM.removeElementClass(self.tab_element, 'selected');
    },
});


zeit.cms.ViewTab = zeit.cms.Tab.extend({

    _options: {
        render_on_activate: false,
    },

    construct: function(id, title, view, options) {
        var self = this;
        self.rendered = false;
        arguments.callee.$.construct.call(self, id, title);
        self.view = view;
        self.options = MochiKit.Base.update(
            MochiKit.Base.clone(self._options), options);
    },

    activate: function() {
        var self = this;
        if (!self.rendered || self.options.render_on_activate) {
            self.view.render();
            self.rendered = true;
        }
        arguments.callee.$.activate.call(self);
    },

});


(function() {
    
    var tab_check = function(element) {
        return element.nodeName == 'A' && element.href.indexOf('tab://') == 0
    };

    var tab_activate = function(element) {
        var tab_id = element.href.substring(6);
        zeit.cms.all_tabs[tab_id].tabs.activate(tab_id);
    }

    zeit.cms.url_handlers.register('tab', tab_check, tab_activate)
})();
