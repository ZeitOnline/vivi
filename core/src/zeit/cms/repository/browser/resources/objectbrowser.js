if (isUndefinedOrNull(zeit.cms.repository)) {
    zeit.cms.repository = {}
}


zeit.cms.repository.ObjectBrowser = gocept.Class.extend({

    construct: function(lightbox_form) {
        var self = this;
        self.lightbox_form = lightbox_form;
        self.content_box = lightbox_form.lightbox.content_box;
        self.events = []
        self.events.push(MochiKit.Signal.connect(
            self.content_box, 'onclick', self, self.handle_click));
        self.events.push(MochiKit.Signal.connect(
            self.lightbox_form, 'before-close', self, self.destruct));

        var url = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'tree-view-url', self.content_box).innerHTML;
        self.navtree = new Tree(url, 'popup-navtree');
        var scroll_state = new zeit.cms.ScrollStateRestorer('popup-navtree');
        scroll_state.restoreScrollState();
    },

    destruct: function() {
        var self = this;
        self.navtree.destruct();
        while (self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        }
    },

    load: function(url) {
        var self = this;
        var scroll_state = new zeit.cms.ScrollStateRestorer('popup-navtree');
        scroll_state.rememberScrollState();
        self.destruct();
        self.lightbox_form.url = url + '/@@get_object_browser';
        self.lightbox_form.reload();
    },

    select_object: function(unique_id) {
        var self = this;
        MochiKit.Signal.signal(
            self.lightbox_form,
            'zeit.cms.ObjectReferenceWidget.selected', unique_id);
    },

    handle_click: function(event) {
        var self = this;
        var stop = true;
        log('click');
        if (event.target().nodeName == 'A') {
            self.load(event.target().href);
        } else if (event.target().nodeName == 'TD') {
            var tr = event.target().parentNode;
            var url_node = MochiKit.DOM.getFirstElementByTagAndClassName(
                'span', 'uniqueId', tr);
            if (url_node) {
                self.select_object(url_node.textContent);
            }
        } else {
            stop = false;
        }
        if (stop) {
            event.stop();
        }
    },

});
