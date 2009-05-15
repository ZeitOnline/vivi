zeit.cms.Tabs = gocept.Class.extend({
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
        var self = this;
        tab.after_add(self);
        self.tabs.push(tab);
        if (self.tabs.length == 1) {
            tab.activate();
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
                tab.activate();
            } else {
                tab.deactivate();
            }
        });
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
        self.tab_element = parent.tabs_element.appendChild(
            LI({},
                A({href: self.id}, self.title)))
        self.container = parent.container.appendChild(DIV({id: self.id}));
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
    construct: function(id, title, view) {
        var self = this;
        arguments.callee.$.construct.call(self, id, title);
        self.view = view;
    },

    activate: function() {
        var self = this;
        self.view.render();
        arguments.callee.$.activate.call(self);
    },
});
