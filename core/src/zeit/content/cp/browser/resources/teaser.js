zeit.content.cp.teaser = {};

zeit.content.cp.teaser.Sortable = zeit.content.cp.Sortable.extend({

    __name__: 'zeit.content.cp.teaser.Sortable',
    context: zeit.content.cp.in_context.Lightbox,

    construct: function() {
        var self = this;
        var container_id = 'teaser-list-edit-box-sorter';
        self.parent = zeit.content.cp.getParentComponent($(container_id));
        arguments.callee.$.construct.call(self, container_id);
    },

    connect: function() {
        var self = this;
        arguments.callee.$.connect.call(self);
        self.activate_content_droppers();
    },

    get_sortable_nodes: function() {
        var self = this;
        return elements = MochiKit.Selector.findChildElements(
            $(self.container), ['li.edit-bar'])
    },

    serialize: function() {
        var self = this;
        return MochiKit.Base.map(
            function(e) { return e.getAttribute('cms:uniqueId')},
            self.get_sortable_nodes());
    },

    on_update: function(element) {
        var self = this;
        var d = arguments.callee.$.on_update.call(self);
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self.parent, 'reload');
        });
        return d;
    },

    activate_content_droppers: function() {
        var self = this;
        var elements = MochiKit.Selector.findChildElements(
            $(self.container),
            ['li.action-content-droppable']);
        forEach(elements, function(element) {
            var url = element.getAttribute('cms:drop-url');
            self.dnd_objects.push(
                new zeit.content.cp.ContentDropper(
                    element, url, self.parent));
        });
    },
    
});


zeit.content.cp.teaser.TeaserListDeleteEntry = gocept.Class.extend({
    // Delete entry from teaser list

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        self.parent = zeit.content.cp.getParentComponent(context_element);
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self.parent, 'reload');
        });
    },
});


zeit.content.cp.teaser.TeaserEditBox = zeit.content.cp.LightBoxForm.extend({

    __name__: 'zeit.content.cp.teaser.TeaserEditBox',

    clean: false,
    
    on_close: function() {
        var self = this;
        var super = arguments.callee.$.on_close
        if (self.clean) {
            super.call(self);
        } else {
            var d = self.remove_checked_out();
            d.addBoth(function(result_or_error) {
                super.call(self);
                return result_or_error
            });
        }
    },

    remove_checked_out: function() {
        var self = this;
        return MochiKit.Async.doSimpleXMLHttpRequest(self.cleanup_url);
    },

});
