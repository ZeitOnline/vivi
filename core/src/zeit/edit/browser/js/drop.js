(function() {

zeit.cms.declare_namespace('zeit.edit.drop');


zeit.edit.drop.DropHandler = gocept.Class.extend({

    construct: function(options) {
        var self = this;
        MochiKit.Base.update(self, options);
    },

});


zeit.edit.drop.handlers = [];
zeit.edit.drop.handler_by_accept = {}
zeit.edit.drop.handler_by_activation = {}


zeit.edit.drop.registerHandler = function(options) {
    var handler = new zeit.edit.drop.DropHandler(options);
    zeit.edit.drop.handlers.push(handler);
    forEach(options.accept, function(accept_class) {
        zeit.edit.drop.handler_by_accept[accept_class] = handler;
    });
    zeit.edit.drop.handler_by_activation[handler.activated_by] = handler;
    return handler;
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
        self.droppable = new MochiKit.DragAndDrop.Droppable(droppable_element, {
            accept: accept,
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(draggable, droppable, event) {
                return self.drop(draggable, droppable, data_element);
            },
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

        var d = zeit.edit.makeJSONRequest(url, query_args, self.parent)
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
    },

});


zeit.edit.drop.EditorDroppers = 
    zeit.edit.context.ContentActionBase.extend({

    __name__: 'zeit.edit.drop.EditorDroppers',
    context: zeit.edit.context.Editor,

    connect: function() {
        var self = this;
        var selectors = MochiKit.Base.map(
            function(h) {
                return '.' + h.activated_by;
            }, zeit.edit.drop.handlers);

        var elements = MochiKit.Selector.findChildElements(
            self.editor.content, selectors);
        forEach(elements, function(element) {
            var droppable_element = self.get_droppable_element_for(element);
            self.dnd_objects.push(
                new zeit.edit.drop.Droppable(
                    droppable_element, element, zeit.edit.editor));
        });
    },

    get_droppable_element_for: function(element) {
        if (MochiKit.DOM.hasElementClass(element, 'landing-zone')) {
            return element;
        }
        var block = MochiKit.DOM.getFirstParentByTagAndClassName(
            element, null, 'block');
        return block;
    },

});


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.edit.drop.droppers = new zeit.edit.drop.EditorDroppers();
});


zeit.edit.drop.content_drop_handler = 
    zeit.edit.drop.registerHandler({
        accept: ['uniqueId', 'content-drag-pane'],
        activated_by: 'action-content-droppable',
        url_attribute: 'cms:drop-url',
        query_arguments: function(draggable) {
            var query = {'uniqueId': draggable.uniqueId}
            MochiKit.Base.update(query, draggable.drop_query_args);
            return query;
        }
});

})();
