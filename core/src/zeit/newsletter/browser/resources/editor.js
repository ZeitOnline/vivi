(function($) {

zeit.cms.declare_namespace('zeit.newsletter');


zeit.cms.in_newsletter_editor = function() {
    return Boolean($('.newsletter-editor-inner').length);
};


zeit.newsletter.TeaserSorter = gocept.Class.extend({

    __name__: 'zeit.newsletter.TeaserSorter',

    construct: function() {
        var self = this;
        new zeit.edit.context.Editor(self);
        self.container = '.block.type-group > .block-inner';
    },

    connect: function() {
        var self = this;

        $(self.container).sortable({
            connectWith: self.container,
            handle: '.dragger',
            items: '> .block',
            update: function(event, ui) {
                var container = $(event.target);
                var item = $(ui.item);
                // the DOM has already changed when we are called, so the
                // item already has a new parent if it was moved between
                // containers.
                var is_remove = item.parent()[0] != container[0];
                var is_receive = ui.sender;
                if (is_remove || is_receive) {
                    return;
                }
                self.update_order(container);
            },

            receive: function(event, ui) {
                var item = $(ui.item);
                var source = $(ui.sender);
                var destination = $(event.target);
                self.move(item, source, destination);
            }
        });
    },

    disconnect: function() {
        var self = this;
        $(self.container).sortable('destroy');
    },

    update_order: function(container) {
        var self = this;
        var data = MochiKit.Base.serializeJSON({
            keys: self.serialize(container)
        });
        var block = container.parent();
        var url = block.attr('cms:url');
        var d = MochiKit.Async.doXHR(url + '/@@updateOrder', {
            method: 'POST',
            sendContent: data});

        d.addCallback(function(result) {
            self.reload(container);
        });
        d.addErrback(zeit.edit.handle_json_errors);

        return d;
    },

    move: function(item, source, destination) {
        var self = this;
        var data = MochiKit.Base.serializeJSON({
            key: item.attr('id')
        });
        var block = destination.parent();
        var url = block.attr('cms:url');
        var d = MochiKit.Async.doXHR(url + '/@@move', {
            method: 'POST',
            sendContent: data});

        d.addCallback(function(result) {
            self.update_order(destination);
        });
        d.addCallback(function(result) {
            self.reload(source);
        });
        d.addErrback(zeit.edit.handle_json_errors);

        return d;
    },

    reload: function(container) {
        var self = this;
        var block = container.parent();
        var url = block.attr('cms:url');
        MochiKit.Signal.signal(
            zeit.edit.editor, 'reload', block.attr('id'), url + '/@@contents');
    },

    serialize: function(container) {
        return container.find('> .block').map(function(i, elem) {
            return $(elem).attr('id');
        });
    }

});


var ident = MochiKit.Signal.connect(
    window, 'script-loading-finished', function() {
        MochiKit.Signal.disconnect(ident);
        if (! zeit.cms.in_newsletter_editor()) {
            return;
        }
        zeit.newsletter.group_sorter = new zeit.edit.sortable.BlockSorter(
            'newsletter_body');
        zeit.newsletter.teaser_sorter = new zeit.newsletter.TeaserSorter();
});

})(jQuery);