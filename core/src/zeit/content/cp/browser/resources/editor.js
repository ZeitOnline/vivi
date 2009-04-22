if (isUndefinedOrNull(zeit.content)) {
    zeit.content = {}
}
zeit.content.cp = {}


zeit.content.cp.resolveDottedName = function(name) {
    // Resolve *absolute* dotted name
    var obj = window;
    forEach(name.split('.'), function(step) {
        obj = obj[step]
    });
    return obj;
}


zeit.content.cp.getParentComponent = function(context_element) {
    var parent = null;
    var parent_element = context_element.parentNode;
    while (!isNull(parent_element) && isUndefinedOrNull(parent)) {
        parent = parent_element.__handler__;
        parent_element = parent_element.parentNode;
    }
    return parent;
}


zeit.content.cp.Editor = gocept.Class.extend({
    
    construct: function() {
        var self = this;
        self.content = $('cp-content');
        self.content.__handler__ = self;
        MochiKit.Signal.connect(
            'content', 'onclick',
            self, 'handleContentClick');
        MochiKit.Signal.connect(
            self, 'reload', self, 'reload');
    },

    handleContentClick: function(event) {
        var self = this;
        log("Target " + event.target().nodeName);
        var module_name = event.target().getAttribute('cms:cp-module')
        if (module_name) {
            log("Loading module " + module_name);
            event.stop();
            var module = zeit.content.cp.resolveDottedName(module_name);
            new module(event.target());
        } else if (event.target().nodeName != 'INPUT') {
            event.preventDefault();
        }
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        var url = context_url + '/contents';
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            self.content.innerHTML = result.responseText;
            MochiKit.Signal.signal(self, 'after-reload');
        });
    },
});


(function() {
    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        if (isNull($('cp-content'))) {
            return
        }
        zeit.content.cp.editor = new zeit.content.cp.Editor();
        MochiKit.Signal.signal(window, 'cp-editor-initialized');
        zeit.content.cp.editor.reload();
    });
})();


zeit.content.cp.BlockHover = gocept.Class.extend({

    construct: function() {
        var self = this;
        MochiKit.Signal.connect('cp-content', 'onmouseover', self, self.over);
        MochiKit.Signal.connect('cp-content', 'onmouseout', self, self.out);
    },

    over: function(event) {
        var self = this;
        var block = self.get_block(event.target());
        if (!isNull(block)) {
            MochiKit.DOM.addElementClass(block, 'hover');
        }
    },

    out: function(event) {
        var self = this;
        var block = self.get_block(event.target());
        if (!isNull(block)) {
            MochiKit.DOM.removeElementClass(block, 'hover');
        }
    },

    get_block: function(element) {
        var class = 'block';
        if (MochiKit.DOM.hasElementClass(element, class)) {
            return element
        }
        return MochiKit.DOM.getFirstParentByTagAndClassName(
            element, null, class);
    },
});

MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.content.cp.block_hover = new zeit.content.cp.BlockHover();
});


//
// Define context managers
//
zeit.content.cp.in_context = {};


zeit.content.cp.in_context.Base = gocept.Class.extend({

    __name__: 'zeit.content.cp.in_context.Base',

    construct: function(context_aware) {
        var self = this;
        log("Creating " + self.__name__ + " for " + context_aware.__name__)
        self.context_aware = context_aware;
        self.events = [];
        
        self.init();

        self.events.push(MochiKit.Signal.connect(
            zeit.content.cp.editor, 'single-context-start',
            self, self.deactivate));
        self.events.push(MochiKit.Signal.connect(
            zeit.content.cp.editor, 'single-context-end',
            self, self.activate));
    },

    destroy: function() {
        var self = this;
        while(self.events.length) {
          MochiKit.Signal.disconnect(self.events.pop());
        }
    },

    activate: function() {
        var self = this;
        log('Activating ' + self.context_aware.__name__);
        self.context_aware.connect.call(self.context_aware);
    },

    deactivate: function() {
        var self = this;
        log('Deactivating ' + self.context_aware.__name__);
        self.context_aware.disconnect.call(self.context_aware);
    },
});


zeit.content.cp.in_context.Editor = zeit.content.cp.in_context.Base.extend({

    __name__: 'zeit.content.cp.in_context.Editor',

    init: function() {
        var self = this;
        // Those handlers stay forever
        self.events.push(MochiKit.Signal.connect(
            zeit.content.cp.editor, 'after-reload',
            self, self.activate));
        self.events.push(MochiKit.Signal.connect(
            zeit.content.cp.editor, 'before-reload',
            self, self.deactivate));
    },

});


zeit.content.cp.in_context.Lightbox = zeit.content.cp.in_context.Base.extend({

    __name__: 'zeit.content.cp.in_context.Lightbox',

    init: function() {
        var self = this;
        MochiKit.Signal.signal(zeit.content.cp.editor, 'single-context-start');
        self.activate();
        self.events.push(MochiKit.Signal.connect(
            self.context_aware, 'before-close',
            self, self.deactivate));
        self.events.push(MochiKit.Signal.connect(
            self.context_aware, 'before-reload',
            self, self.deactivate));
    },

    deactivate: function() {
        var self = this;
        arguments.callee.$.deactivate.call(self);
        self.destroy();
    },
});


zeit.content.cp.ContentActionBase = gocept.Class.extend({

    __name__: 'zeit.content.cp.ContentActionBase',
    context: null,  // define in sublcasses

    construct: function() {
        var self = this;
        self.editor = zeit.content.cp.editor;
        self.dnd_objects = [];
        self.events = [];
        if (isNull(self.context)) {
            log("No context for "+self.__name__);
        } else {
            new self.context(self);
        }
    },

    disconnect: function() {
        var self = this;
        while(self.dnd_objects.length) {
          self.dnd_objects.pop().destroy();
        }
        while(self.events.length) {
          MochiKit.Signal.disconnect(self.events.pop());
        }
    },

});


zeit.content.cp.ContentDropper = zeit.content.cp.ContentActionBase.extend({
    // Handle dropping of content objects.

    __name__: 'zeit.content.cp.ContentDropper',
    context: zeit.content.cp.in_context.Editor,

    connect: function() {
        var self = this;
        var elements = MochiKit.Selector.findChildElements(
            self.editor.content,
            ['div.action-content-droppable']);
        forEach(elements, function(element) {
            var block = MochiKit.DOM.getFirstParentByTagAndClassName(
                element, null, 'block'); 
            var url = element.getAttribute('cms:drop-url');
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Droppable(block, {
                    hoverclass: 'hover-content',
                    ondrop: function(draggable, droppable, event) {
                        self.drop(draggable, droppable, event, url);
                    },
                }));
        });
    },

    drop: function(draggable, droppable, event, url) {
        var self = this;
        var uniqueId = draggable.uniqueId;
        if (isUndefinedOrNull(uniqueId)) {
            return
        }
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            url, {'uniqueId': uniqueId});
        // XXX error handling
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self.editor, 'reload');
        });
        
    },
});


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.content.cp.content_dropper = new zeit.content.cp.ContentDropper();
});


zeit.content.cp.Sortable = zeit.content.cp.ContentActionBase.extend({
    // Sorting support.

    __name__: 'zeit.content.cp.Sortable',
    default_options: {
        onChange: MochiKit.Base.noop,
        scroll: 'cp-content',
    },

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
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Draggable(node, {
                    constraint: 'vertical',
                    handle: handle,
                    ghosting: false,
                    revert: true,
                    scroll: self.options()['scroll'],
                    //selectclass: 'hover',
                    zindex: 10000,
            }));
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Droppable(node, {
                    containment: [container],
                    onhover: MochiKit.Sortable.onHover,
                    overlap: 'vertical',
           }));
        });
        
        self.options().lastValue = self.serialize();
        this.events.push(MochiKit.Signal.connect(
            MochiKit.DragAndDrop.Draggables, 'start',
            function(draggable) { self.on_start(container, draggable); }));
        this.events.push(MochiKit.Signal.connect(
            MochiKit.DragAndDrop.Draggables, 'end',
            function(draggable) { self.on_end(container, draggable); }));
    },

    on_start: function(element, draggable) {
        var self = this;
        self.options().lastValue = self.serialize();
    },

    on_end: function(element, draggable) {
        var self = this;
        MochiKit.Sortable.unmark();
        if (!MochiKit.Base.arrayEqual(self.options().lastValue,
                                      self.serialize())) {
            self.on_update(element);
        }
        element.style.zIndex = null;  // see #4999
    },

    on_update: function(element) {
        var self = this;
        var keys = MochiKit.Base.serializeJSON(self.serialize());
        var url = $(self.container).getAttribute('cms:url') + '/@@updateOrder';
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url, {keys:keys});
        // We don't have do anything on success as the ordering is already
        // applied in the HTML.
        // XXX error handling!
        return d;
    },


    get_handle: function(element) {
        return null;  // make the whole element draggable
    },

    serialize: function() {
        var self = this;
        return MochiKit.Base.map(
            function(e) { return e.id }, self.get_sortable_nodes());
    },

    options: function() {
        var self = this;
        return MochiKit.Sortable.options(self.container)
    },

});


zeit.content.cp.TeaserBarSorter = zeit.content.cp.Sortable.extend({

    __name__: 'zeit.content.cp.TeaserBarSorter',
    context: zeit.content.cp.in_context.Editor,

    construct: function() {
        var self = this;
        arguments.callee.$.construct.call(self, 'cp-teasermosaic');
    },

    get_sortable_nodes: function() {
        var self = this;
        return MochiKit.Selector.findChildElements(
            self.editor.contents,
            ['#cp-teasermosaic > div.block.type-teaser-bar']);
    },

    get_handle: function(element) {
        return MochiKit.Selector.findChildElements(
            element, ['> .block-inner > .edit > .dragger'])[0];
    },
});


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.content.cp.teaser_bar_sorter = new zeit.content.cp.TeaserBarSorter();
});


zeit.content.cp.LightBoxForm = zeit.cms.LightboxForm.extend({

    construct: function(context_element) {
        var self = this;
        self.context_element = context_element;
        var container_id = context_element.getAttribute('cms:lightbox-in');
        self.parent = zeit.content.cp.getParentComponent(context_element);
        var url = context_element.getAttribute('href');
        arguments.callee.$.construct.call(self, url, $(container_id));
        self.lightbox.content_box.__handler__ = self;

        self.events.push(MochiKit.Signal.connect(
           zeit.content.cp.editor, 'before-reload',
           self, 'close'));
        self.close_event_handle = MochiKit.Signal.connect(
            self.lightbox, 'before-close',
            self, self.on_close);
        self.events.push(
            MochiKit.Signal.connect(
                self, 'reload', self, self.reload));
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        arguments.callee.$.reload.call(self);
    },

    handle_submit: function(action) {
        var self = this;
        var d = arguments.callee.$.handle_submit.call(self, action)
        d.addCallback(function(result) {
            if (isNull(result)) {
                return null;
            }
            var summary = MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'summary', self.form);
            if (isNull(summary)) {
                return result;
            }
            self.close();
        });
    },

    on_close: function() {
        var self = this;
        MochiKit.Signal.disconnect(self.close_event_handle);
        MochiKit.Signal.signal(self.parent, 'reload');
    },
});


zeit.content.cp.LoadAndReload = gocept.Class.extend({

    construct: function(context_element) {
        var url = context_element.getAttribute('href');
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            MochiKit.Signal.signal(zeit.content.cp.editor, 'reload');
        });
    },

});


zeit.content.cp.ConfirmDelete = gocept.Class.extend({

    construct: function(context_element) {
        var self = this;
        self.parent = zeit.content.cp.getParentComponent(context_element);
        var url = context_element.getAttribute('href');
        // XXX i18n
        var delete_module = context_element.getAttribute('cms:delete-module');
        var highlight_class = context_element.getAttribute(
            'cms:delete-highlight')
        self.confirm = DIV(
            {'class': 'confirm-delete'},
            A({'href': url,
               'cms:cp-module': delete_module},
               'Remove'))
        context_element.appendChild(self.confirm);
        MochiKit.Visual.appear(self.confirm)
        self.block = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, null, highlight_class);
        MochiKit.DOM.addElementClass(self.block, 'highlight');

        self.overlay = DIV({'id': 'confirm-delete-overlay'});
        $('body').appendChild(self.overlay);
        self.events = []
        self.events.push(
            MochiKit.Signal.connect(self.overlay, 'onclick', self, 'close'));
        self.events.push(
            MochiKit.Signal.connect(
                self.parent, 'before-reload', self, 'close'))

    },

    close: function(event) {
        var self = this;
        MochiKit.Base.map(
            MochiKit.Signal.disconnect, self.events)
        self.confirm.parentNode.removeChild(self.confirm);
        self.overlay.parentNode.removeChild(self.overlay);
        MochiKit.DOM.removeElementClass(self.block, 'highlight');
    },
})
