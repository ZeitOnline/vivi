(function() {

zeit.edit.LightBoxForm = zeit.cms.LightboxForm.extend({

    __name__: 'zeit.edit.LightBoxForm',
    context: zeit.edit.context.Lightbox,

    construct: function(context_element) {
        var self = this;
        self.context_element = context_element;
        var container_id = context_element.getAttribute('cms:lightbox-in');
        self.parent = zeit.edit.getParentComponent(context_element);
        var url = context_element.getAttribute('href');
        self.reload_id = context_element.getAttribute(
            'cms:lightbox-reload-id');
        self.reload_url = context_element.getAttribute(
            'cms:lightbox-reload-url');
        arguments.callee.$.construct.call(self, url, $(container_id));
        self.lightbox.content_box.__handler__ = self;
        self.reload_parent_component_on_close = true;
        new self.context(self);
    },

    connect: function() {
        var self = this;
        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'before-reload', function() {
                self.reload_parent_component_on_close = false;
                self.close();
        }));
        self.close_event_handle = MochiKit.Signal.connect(
            self.lightbox, 'before-close',
            self, self.on_close);
        self.events.push(
            MochiKit.Signal.connect(
                self, 'reload', self, self.reload));
    },

    disconnect: function() {
        // hum, do we need to do anything here? We use the lightbox events
        // right now.
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        var d = arguments.callee.$.reload.call(self);
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self, 'after-reload');
            return result;
        });
        return d;
    },

    on_close: function() {
        var self = this;
        log("closing lightbox");
        MochiKit.Signal.disconnect(self.close_event_handle);
        MochiKit.Signal.signal(self, 'before-close');
        if (self.reload_parent_component_on_close) {
            MochiKit.Signal.signal(
                self.parent, 'reload',
                self.reload_id, self.reload_url);
        }
    }
});


zeit.edit.TabbedLightBoxForm = zeit.edit.LightBoxForm.extend({

    __name__: 'zeit.edit.TabbedLightBoxForm',

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        if (!isUndefinedOrNull(self.tabs)) {
            self.tabs.active_tab.view.render();
            return;
        }
        var tab_definitions = MochiKit.DOM.getElementsByTagAndClassName(
                null, 'lightbox-tab-data', self.context_element.parentNode);
        var i = 0;
        self.tabs = new zeit.cms.Tabs(
                self.lightbox.content_box);
        forEach(tab_definitions, function(tab_definition) {
            var tab_id = 'tab-'+i;
            var tab_view = new zeit.cms.View(
                    tab_definition.href, tab_id);
            var tab = new zeit.cms.ViewTab(
                tab_id, tab_definition.title, tab_view);
            self.tabs.add(tab);
            self.events.push(
                MochiKit.Signal.connect(
                    tab_view, 'load', function() {
                    self.form = MochiKit.DOM.getFirstElementByTagAndClassName(
                        'form', null, $(tab_view.target_id));
                    if (!isNull(self.form)) {
                        self.rewire_submit_buttons();
                    }
                    $(tab_view.target_id).__handler__ = self;
                    self.eval_javascript_tags();
                    MochiKit.Signal.signal(self, 'after-reload');
            }));
            if (self.context_element == tab_definition) {
                self.tabs.activate(tab_id);
            }
            i = i + 1;
        });
    }

});

}());