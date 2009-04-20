zeit.content.cp.teaser = {};

zeit.content.cp.teaser.Sortable = zeit.content.cp.Sortable.extend({

    __name__: 'zeit.content.cp.teaser.Sortable',
    context: zeit.content.cp.in_context.Lightbox,

    construct: function() {
        var self = this;
        arguments.callee.$.construct.call(
            self, 'teaser-list-edit-box-sorter');
    },

    get_sortable_nodes: function() {
        var self = this;
        return MochiKit.Sortable.findChildren(
            $(self.container), null, false, 'li');
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
            zeit.content.cp.lightbox.reload();
        });
        return d;
    },
    
});


zeit.content.cp.teaser.TeaserListDeleteEntry = gocept.Class.extend({
    construct: function(context_element) {
        var url = context_element.getAttribute('href');
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            zeit.content.cp.lightbox.reload();
        });
    },
});
