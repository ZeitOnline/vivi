(function() {

zeit.cms.declare_namespace('zeit.edit.drop');


zeit.edit.drop.DropHandler = gocept.Class.extend({

    construct: function(options) {
        var self = this;
        MochiKit.Base.update(self, options);
    }

});


zeit.edit.drop.handlers = [];
zeit.edit.drop.handler_by_accept = {};
zeit.edit.drop.handler_by_activation = {};


zeit.edit.drop.registerHandler = function(options) {
    var handler = new zeit.edit.drop.DropHandler(options);
    zeit.edit.drop.handlers.push(handler);
    forEach(options.accept, function(accept_class) {
        zeit.edit.drop.handler_by_accept[accept_class] = handler;
    });
    zeit.edit.drop.handler_by_activation[handler.activated_by] = handler;
    return handler;
};


zeit.edit.drop.registerContentHandler = function(options) {
    options.url_attribute = options.url_attribute || 'cms:drop-url';
    options.query_arguments = options.query_arguments || function(draggable) {
        // the draggables are provided by zeit.cms.browser:js/dnd.js,
        // see there for their structure
        var query = {'uniqueId': draggable.uniqueId};
        MochiKit.Base.update(query, draggable.drop_query_args);
        return query;
    };
    return zeit.edit.drop.registerHandler(options);
};


zeit.edit.drop.Droppable = gocept.Class.extend({
    // Handle dropping of content objects.

    __name__: 'zeit.edit.drop.Droppable',

    construct: function(droppable_element, data_element, parent) {
        var self = this;
        var accept = [];
        forEach(
            MochiKit.Base.keys(zeit.edit.drop.handler_by_activation),
            function(css_class) {
            if (MochiKit.DOM.hasElementClass(data_element, css_class)) {
                var handler = zeit.edit.drop.handler_by_activation[
                    css_class];
                MochiKit.Base.extend(accept, handler.accept);
            }
        });
        self.droppable = new zeit.cms.ContentDroppable(droppable_element, {
            accept: accept,
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(draggable, droppable, event) {
                return self.drop(draggable, droppable, data_element);
            }
        });
        self.parent = parent;
    },

    destroy: function() {
        var self = this;
        self.droppable.destroy();
        delete self.droppable;
    },

    drop: function(draggable_element, droppable, data_element) {
        var self = this;
        var handler = self.get_handler(draggable_element);
        var url = data_element.getAttribute(handler.url_attribute);
        var query_args = handler.query_arguments(draggable_element);

        // Since MochiKit does not differentiate whether we successfullly
        // landed on a Droppable or not, we need to make that distinction
        // ourselves.
        draggable_element.drag_successful = true;

        var d = zeit.edit.makeJSONRequest(url, query_args, self.parent);
        d.addCallback(function(result) {
            MochiKit.Signal.signal(
                handler, 'drop-finished',
                draggable_element, droppable, data_element);
            return result;
        });
        return d;
    },

    get_handler: function(draggable_element) {
        var handler = null;
        forEach(
            MochiKit.Base.keys(zeit.edit.drop.handler_by_accept),
            function(css_class) {
                if(MochiKit.DOM.hasElementClass(draggable_element, css_class)) {
                    handler = css_class;
                    throw MochiKit.Iter.StopIteration;
                }
            });
        return zeit.edit.drop.handler_by_accept[handler];
    }

});


zeit.edit.drop.revert_unless_successful = function(draggable_element) {
    return ! draggable_element.drag_successful;
};


zeit.edit.drop.EditorDroppers =
    zeit.edit.context.ContentActionBase.extend({

    __name__: 'zeit.edit.drop.EditorDroppers',
    context: zeit.edit.context.Editor,

    connect: function() {
        var self = this;
        var selectors = MochiKit.Base.map(
            function(h) {
                return '.' + h.activated_by;
            }, zeit.edit.drop.handlers).join(',');

        jQuery(selectors, self.editor.content).each(function(i, element) {
            var droppable_element = self.get_droppable_element_for(element);
            self.dnd_objects.push(
                new zeit.edit.drop.Droppable(
                    droppable_element, element, zeit.edit.editor));
        });

        self.resume_drag_in_progress();
    },

    resume_drag_in_progress: function () {
        var drag_pane = $('drag-pane');
        if (!drag_pane ||
            MochiKit.DOM.hasElementClass(drag_pane, 'finished')) {
            return;
        }
        MochiKit.DragAndDrop.Droppables.prepare(drag_pane);
    },

    get_droppable_element_for: function(element) {
        if (MochiKit.DOM.hasElementClass(element, 'landing-zone')) {
            return element;
        }
        var block = MochiKit.DOM.getFirstParentByTagAndClassName(
            element, null, 'block');
        return block;
    }

});


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.edit.drop.droppers = new zeit.edit.drop.EditorDroppers();
});


zeit.edit.drop.content_drop_handler = zeit.edit.drop.registerContentHandler({
    accept: ['uniqueId', 'content-drag-pane'],
    activated_by: 'action-content-droppable'
});

}());
