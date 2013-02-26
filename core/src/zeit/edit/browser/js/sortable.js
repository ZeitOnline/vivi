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

    construct: function(container, passed_options) {
        var self = this;
        self.container = container;
        var options = MochiKit.Base.update(
            MochiKit.Base.clone(self.default_options), passed_options);
        MochiKit.Sortable.sortables[container] = options;
        arguments.callee.$.construct.call(self);
    },

    connect: function() {
        var self = this;
        var container = $(self.container);

        var nodes = self.get_sortable_nodes();
        forEach(nodes, function(node) {
            var handle = self.get_handle(node);
            if (handle !== self.NOT_DRAGGABLE) {
                self.dnd_objects.push(
                    new MochiKit.DragAndDrop.Draggable(node, {
                        constraint: self.options()['constraint'],
                        handle: handle,
                        ghosting: false,
                        revert: true,
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
        self.options().lastValue = null;
        zeit.cms.request_lock.acquire().addCallback(function() {
            self.options().lastValue = self.serialize();
        });
    },

    on_end: function(element, draggable) {
        var self = this;
        MochiKit.Sortable.unmark();
        if (!MochiKit.Base.arrayEqual(self.options().lastValue,
                                      self.serialize())) {
            self.on_update(element);
        }
        zeit.cms.request_lock.release();
        element.style.zIndex = null;  // see #4999
    },

    on_update: function(element) {
        var self = this;
        var data = MochiKit.Base.serializeJSON({
            keys: self.serialize()
        });
        var url = self.options()['update_url'];
        if (isUndefinedOrNull(url)) {
            url = $(self.container).getAttribute(
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
        return MochiKit.Sortable.options(self.container);
    }

});


zeit.edit.sortable.BlockSorter = zeit.edit.sortable.Sortable.extend({
    // Specialized block sorting

    __name__: 'zeit.edit.sortable.BlockSorter',
    context: zeit.edit.context.Editor,

    construct: function(container_id, passed_options) {
        var self = this;
        arguments.callee.$.construct.call(self, container_id, passed_options);
    },

    get_sortable_nodes: function() {
        var self = this;
        var selector = '#' + self.container + ' > div.block[id]';
        return $$(selector);
    },

    get_handle: function(element) {
        var self = this;
        var result = MochiKit.Selector.findChildElements(
            element, ['> .block-inner > .edit > .dragger']);
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
                url = $(self.container).getAttribute(
                    'cms:url') + '/@@contents';
            }
            var reload_id = self.options()['reload_id'];
            if (isUndefinedOrNull(reload_id)) {
                reload_id = self.container;
            }
            MochiKit.Signal.signal(
                self.editor, 'reload', reload_id, url);
            return result;
        });
        return d;
    }
});
