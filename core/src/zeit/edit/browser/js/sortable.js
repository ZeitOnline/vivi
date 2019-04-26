zeit.cms.declare_namespace('zeit.edit.sortable');


zeit.edit.sortable.Sortable = zeit.edit.context.ContentActionBase.extend({
    // General sorting support.

    __name__: 'zeit.edit.sortable.Sortable',
    default_options: {
        constraint: 'vertical',
        onChange: MochiKit.Base.noop,
        overlap: 'vertical',
        scroll: 'cp-content-inner'
    },

    NOT_DRAGGABLE: {},

    /*

    We must differentiate between the container with meta data and the
    container which contains draggable children, since the HTML may contain a
    node between parent and children, thus they are not direct decendents.

    Arguments:
      container_id ... ID selector without leading #,
                       DOM element should contain target URL,
                       options will be stored there
      child_container_selector ... complete selector of the DOM element that
                                   contains the draggable children
    */
    construct: function(container_id, child_container_selector,
                        override_options) {
        var self = this;
        self.container_id = container_id;
        if (child_container_selector) {
            self.child_container_selector = child_container_selector;
        } else {
            self.child_container_selector = '#' + self.container_id;
        }
        var options = MochiKit.Base.update(
            MochiKit.Base.clone(self.default_options), override_options);
        MochiKit.Sortable.sortables[container_id] = options;
        arguments.callee.$.construct.call(self);
    },

    connect: function() {
        var self = this;
        var container = jQuery(self.child_container_selector)[0];

        var nodes = self.get_sortable_nodes();
        forEach(nodes, function(node) {
            var handle = self.get_handle(node);
            if (handle !== self.NOT_DRAGGABLE) {
                self.dnd_objects.push(
                    new MochiKit.DragAndDrop.Draggable(node, {
                        constraint: self.options()['constraint'],
                        handle: handle,
                        ghosting: false,
                        revert: zeit.edit.drop.revert_unless_successful,
                        scroll: self.options()['scroll'],
                        //selectclass: 'hover',
                        zindex: 10000
                }));
            }
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Droppable(node, {
                    containment: [container],
                    onhover: MochiKit.Sortable.onHover,
                    overlap: self.options()['overlap']
           }));
        });

        self.options().lastValue = self.serialize();
        self.events.push(MochiKit.Signal.connect(
            MochiKit.DragAndDrop.Draggables, 'start',
            function(draggable) { self.on_start(container, draggable); }));
        self.events.push(MochiKit.Signal.connect(
            MochiKit.DragAndDrop.Draggables, 'end',
            function(draggable) { self.on_end(container, draggable); }));
    },

    on_start: function(element, draggable) {
        var self = this;
        if (self.get_sortable_nodes().indexOf(draggable.element) == -1) {
            // Not dragging one of our elements? Ignore!
            return;
        }
        zeit.cms.request_lock.acquire().addCallback(function() {
            self.locked = true;
            self.options().lastValue = self.serialize();
        });
    },

    on_end: function(element, draggable) {
        var self = this;
        if (!self.locked) {
            return;
        }
        MochiKit.Sortable.unmark();
        if (!MochiKit.Base.arrayEqual(self.options().lastValue,
                                      self.serialize())) {
            self.on_update(element);
        }
        zeit.cms.request_lock.release();
        self.locked = false;
        element.style.zIndex = null;  // see #4999
    },

    on_update: function(element) {
        var self = this;
        var data = MochiKit.Base.serializeJSON({
            keys: self.serialize()
        });
        var url = self.options()['update_url'];
        if (isUndefinedOrNull(url)) {
            url = $(self.container_id).getAttribute(
                'cms:url') + '/@@updateOrder';
        }
        // We already hold the request lock, see on_start()
        var d = MochiKit.Async.doXHR(url, {
            method: 'POST',
            sendContent: data});
        // We don't have do anything on success as the ordering is already
        // applied in the HTML.
        d.addErrback(zeit.edit.handle_json_errors);
        return d;
    },

    get_handle: function(element) {
        return null;  // make the whole element draggable
    },

    serialize: function() {
        var self = this;
        var ids = [];
        forEach(self.get_sortable_nodes(), function(e) {
            if (e.block_ids) {
                // Support merged blocks.
                ids.push.apply(ids, e.block_ids);
            } else {
                ids.push(e.id);
            }
        });
        return ids;
    },

    options: function() {
        var self = this;
        return MochiKit.Sortable.options(self.container_id);
    }

});


zeit.edit.sortable.BlockSorter = zeit.edit.sortable.Sortable.extend({
    // Specialized block sorting

    __name__: 'zeit.edit.sortable.BlockSorter',
    context: zeit.edit.context.Editor,

    get_sortable_nodes: function() {
        var self = this;
        var selector = self.child_container_selector + ' > div.block[id]';
        return jQuery(selector).toArray();
    },

    get_handle: function(element) {
        var self = this;
        var result = jQuery('> .block-inner > .edit > .dragger', element);
        if (result.length) {
            return result[0];
        } else {
            return self.NOT_DRAGGABLE;
        }
    },

    on_update: function(element) {
        var self = this;
        var d = arguments.callee.$.on_update.call(self);
        d.addCallback(function(result) {
            var url = self.options()['reload_url'];
            if (isUndefinedOrNull(url)) {
                url = $(self.container_id).getAttribute(
                    'cms:url') + '/@@contents';
            }
            var reload_id = self.options()['reload_id'];
            if (isUndefinedOrNull(reload_id)) {
                reload_id = self.container_id;
            }
            MochiKit.Signal.signal(
                self.editor, 'reload', reload_id, url);
            return result;
        });
        return d;
    }
});


zeit.edit.sortable.Movable = zeit.edit.context.ContentActionBase.extend({
// This is very similar to Sortable above, except this only registers
// Draggables; the Droppables are set up with zeit.edit.drop.registerHandler.

    __name__: 'zeit.edit.sortable.Movable',

    NOT_DRAGGABLE: {},

    construct: function(container_id, child_container_selector) {
        var self = this;
        self.container_id = container_id;
        self.child_container_selector = child_container_selector;
        self.options = zeit.edit.sortable.Sortable.prototype.default_options;
        arguments.callee.$.construct.call(self);
    },

    connect: function() {
        // XXX Copy&paste of the upper half of Sortable.connect().
        var self = this;
        var container = jQuery(self.child_container_selector)[0];
        var nodes = self.get_movable_nodes();
        forEach(nodes, function(node) {
            var handle = self.get_handle(node);
            if (handle !== self.NOT_DRAGGABLE) {
                self.dnd_objects.push(
                    new MochiKit.DragAndDrop.Draggable(node, {
                        constraint: self.options['constraint'],
                        handle: handle,
                        ghosting: false,
                        revert: zeit.edit.drop.revert_unless_successful,
                        scroll: self.options['scroll'],
                        zindex: 10000
                }));
            }
        });
    },

    get_handle: function(element) {
        return null;  // Make the whole element draggable.
    },

    get_movable_nodes: function() {
        return [];  // Implement in subclass.
    }

});


zeit.edit.sortable.BlockMover = zeit.edit.sortable.Movable.extend({
// XXX This is a complete duplicate of BlockSorter, since all these two do
// is encode the HTML structure of blocks.

    __name__: 'zeit.edit.sortable.BlockMover',
    context: zeit.edit.context.Editor,

    get_movable_nodes: function() {
        var self = this;
        var selector = self.child_container_selector + ' > div.block[id]';
        return jQuery(selector).toArray();
    },

    get_handle: function(element) {
        var self = this;
        var result = jQuery('> .block-inner > .edit > .dragger', element);
        if (result.length) {
            return result[0];
        } else {
            return self.NOT_DRAGGABLE;
        }
    }

});
