zeit.cms.declare_namespace('zeit.content.cp.teaser');

zeit.content.cp.teaser.Sortable = zeit.edit.sortable.Sortable.extend({

    __name__: 'zeit.content.cp.teaser.Sortable',
    context: zeit.edit.context.Lightbox,

    construct: function() {
        var self = this;
        var container_id = 'teaser-list-edit-box-sorter';
        self.parent = zeit.edit.getParentComponent($(container_id));
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
            self.dnd_objects.push(
                new zeit.edit.drop.Droppable(
                    element, element, self.parent));
        });
    },
    
});


zeit.content.cp.teaser.TeaserListDeleteEntry = gocept.Class.extend({
    // Delete entry from teaser list

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        self.parent = zeit.edit.getParentComponent(context_element);
        var d = zeit.edit.makeJSONRequest(url, null, self.parent, {
            method: 'POST',
        });
        // XXX error handling
    },
});


zeit.content.cp.teaser.TeaserEditBox = zeit.edit.LightBoxForm.extend({

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
        zeit.cms.messages.render();
    },

    remove_checked_out: function() {
        var self = this;
        return MochiKit.Async.doSimpleXMLHttpRequest(self.cleanup_url);
    },

});


zeit.content.cp.teaser.Drag = zeit.edit.context.ContentActionBase.extend({

    __name__: 'zeit.content.cp.teaser.Drag',
    context: zeit.edit.context.Editor,

    connect: function() {
        var self = this;
        forEach($$('div.block.type-teaser'), function(teaser) {
            var text =
                MochiKit.DOM.getFirstElementByTagAndClassName( 
                    'div', 'teaser', teaser);
            if (isNull(text)) {
                return
            }
            var image = MochiKit.Selector.findChildElements(
                teaser, ['.teaser-contents > img']);
            if (image.length) {
                image = image[0];
            } else {
                image = null;
            }
            text.removeFromBlock = teaser.id;
            self.dnd_objects.push(
                zeit.cms.createDraggableContentObject(text, {
                    drop_query_args: {relateds: false},
                    scroll: 'cp-content-inner',
                }));
            self.dnd_objects.push(
                zeit.cms.createDraggableContentObject(text, {
                    drop_query_args: {relateds: false},
                    handle: image,
                    scroll: 'cp-content-inner',
                }));
        });
        
    },

});


(function() {
    var remove_from_cp = function(draggable_element, droppable, data_element) {
        // Check if object was dragged from the CP
        var dragged = draggable_element.dragged_element;
        if (!MochiKit.DOM.isChildNode(dragged, 'cp-content')) {
            return
        }
        var block = MochiKit.DOM.getFirstParentByTagAndClassName(
            dragged, 'div', 'block');
        if (isNull(block)) {
            return
        }
        var base_url = block.getAttribute('cms:url');
        var d = zeit.edit.makeJSONRequest(
            base_url + '/@@delete', {uniqueId: draggable_element.uniqueId});
        return d;
    };

    var ident = MochiKit.Signal.connect(
        window, 'script-loading-finished', function() {
        MochiKit.Signal.disconnect(ident);
        zeit.content.cp.teaser.drag = new zeit.content.cp.teaser.Drag();
        MochiKit.Signal.connect(
            zeit.edit.drop.content_drop_handler, 'drop-finished',
            remove_from_cp);
    });
})();
