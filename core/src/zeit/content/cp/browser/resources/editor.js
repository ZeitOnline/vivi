if (isUndefinedOrNull(zeit.content)) {
    zeit.content = {}
}
zeit.content.cp = {}


zeit.content.cp.makeJSONRequest = function(url, options) {
    zeit.content.cp.editor.busy_until_reload();
    var d = MochiKit.Async.doSimpleXMLHttpRequest(url, options);
    d.addCallbacks(function(result) {
        var result_obj = null;
        try {
            var result_obj = MochiKit.Async.evalJSONRequest(result);
        } catch (e if e instanceof SyntaxError) {
        }
        var immediate_actions = [];
        if (!isNull(result_obj)) {
            signals = result_obj['signals'] || [];
            forEach(signals, function(signal) {
                if (isNull(signal.when)) {
                    immediate_actions.push(signal);
                } else {
                    var ident = MochiKit.Signal.connect(
                        zeit.content.cp.editor, signal.when, function() {
                        MochiKit.Signal.disconnect(ident);
                        MochiKit.Signal.signal.apply(
                            this,
                            extend(
                                [zeit.content.cp.editor, signal.name],
                                signal.args));
                    });
                }
            });
        }
        if (immediate_actions.length) {
            immediate_actions.reverse();
            if (!immediate_actions.length) {
                // No actions. We're done.
                seit.content.cp.editor.idle();
            }
            while(immediate_actions.length) {
                var signal = immediate_actions.pop();
                MochiKit.Signal.signal.apply(
                    this,
                    extend([zeit.content.cp.editor, signal.name], signal.args));
            }
        } else {
            MochiKit.Signal.signal(zeit.content.cp.editor, 'reload');
        }
        return result;
    },
    function(error) {
        // XXX log_error should be part of zeit.cms
        zeit.find.log_error(error);
    });
    return d;
}

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
        self.inner_content = null;
        self.content.__handler__ = self;
        self.busy = false;
        MochiKit.Signal.connect(
            'content', 'onclick',
            self, 'handleContentClick');
        MochiKit.Signal.connect(
            self, 'reload', self, 'reload');
        new zeit.cms.ToolTipManager(self.content);
    },

    handleContentClick: function(event) {
        var self = this;
        var target = event.target();
        log("Target " + target.nodeName);
        while (!isNull(target) && target.id != 'content') {
            // Target can be null when it was removed from the dom by a
            // previous event handler (like the lightbox shade)
            var module_name = target.getAttribute('cms:cp-module')
            if (!isNull(module_name)) {
                break;
            }
            target = target.parentNode;
        }
        if (module_name) {
            log("Loading module " + module_name);
            event.stop();
            var module = zeit.content.cp.resolveDottedName(module_name);
            self.current_module = new module(target);
        } else if (event.target().nodeName != 'INPUT') {
            event.preventDefault();
        }
    },

    reload: function(element_id, url) {
        var self = this;
        var element = null;
        if (!isUndefinedOrNull(element_id)) {
             element = $(element_id);
        }
        MochiKit.Signal.signal(self, 'before-reload');
        if (isUndefinedOrNull(url)) {
            url = context_url + '/contents';
        }
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        if (isNull(element)) {
            d.addCallback(function(result) {
                self.replace_whole_editor(result);
                return result;
            });
        } else {
            d.addCallback(function(result) {
                self.replace_element(element, result);
                return result;
            });
        }
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self, 'after-reload');
        });
    },

    replace_whole_editor: function(result) {
        var self = this;
        if (isNull(self.inner_content)) {
            self.content.innerHTML = result.responseText;
            self.inner_content = (
                MochiKit.DOM.getFirstElementByTagAndClassName(
                    'div', 'cp-content-inner', self.content));
        } else {
            var dom = DIV();
            dom.innerHTML = result.responseText;
            var new_inner = (
                MochiKit.DOM.getFirstElementByTagAndClassName(
                    'div', 'cp-content-inner', dom));
            self.inner_content.innerHTML = new_inner.innerHTML;
        }
    },

    replace_element: function(element, result) {
        var self = this;
        var dom = DIV();
        dom.innerHTML = result.responseText;
        MochiKit.DOM.swapDOM(element, dom.firstChild);
    },

    busy_until_reload: function() {
        var self = this;
        if (self.busy) {
            // Already busy
            return;
        }
        self.busy = true;
        MochiKit.Signal.signal(self, 'busy');
        var ident = MochiKit.Signal.connect(self, 'after-reload', function() {
            MochiKit.Signal.disconnect(ident);
            self.idle();
        });
    },

    idle: function() {
        var self = this;
        if (self.busy) {
            self.busy = false;
            MochiKit.Signal.signal(self, 'idle');
        }
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
        if (!isUndefinedOrNull(context_aware.__context__)) {
            throw new Error("Trying to add new context.");
        }
        context_aware.__context__ = self;
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
        self.context_aware.__context__ = null;
        self.context_aware = null;
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
    // Context for a component running *in* a lightbox.
    // The component needs to declare "parent".

    __name__: 'zeit.content.cp.in_context.Lightbox',

    init: function() {
        var self = this;
        MochiKit.Signal.signal(zeit.content.cp.editor, 'single-context-start');
        self.activate();
        self.events.push(MochiKit.Signal.connect(
            self.context_aware.parent, 'before-close',
            self, self.deactivate));
        self.events.push(MochiKit.Signal.connect(
            self.context_aware.parent, 'before-reload',
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
            var droppable_element = self.get_droppable_element_for(element);
            var url = element.getAttribute('cms:drop-url');
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Droppable(droppable_element, {
                    accept: ['uniqueId', 'content-drag-pane'],
                    activeclass: 'droppable-active',
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
        var d = zeit.content.cp.makeJSONRequest(url, {'uniqueId': uniqueId});
        return d;
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
    zeit.content.cp.content_dropper = new zeit.content.cp.ContentDropper();
});


zeit.content.cp.Sortable = zeit.content.cp.ContentActionBase.extend({
    // General sorting support.

    __name__: 'zeit.content.cp.Sortable',
    default_options: {
        constraint: 'vertical',
        onChange: MochiKit.Base.noop,
        overlap: 'vertical',
        scroll: 'cp-content-inner',
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
            log('Creating draggable and droppable for ' + node.id);
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Draggable(node, {
                    constraint: self.options()['constraint'],
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
                    overlap: self.options()['overlap'],
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
        var url = self.options()['update_url'];
        if (isUndefinedOrNull(url)) {
            var url = $(self.container).getAttribute(
                'cms:url') + '/@@updateOrder';
        }
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


zeit.content.cp.BlockSorter = zeit.content.cp.Sortable.extend({
    // Specialized block sorting

    __name__: 'zeit.content.cp.BlockSorter',
    context: zeit.content.cp.in_context.Editor,

    construct: function(container_id, passed_options) {
        var self = this;
        arguments.callee.$.construct.call(self, container_id, passed_options);
    },

    get_sortable_nodes: function() {
        var self = this;
        var selector = '#' + self.container + ' > div.block';
        return $$(selector);
    },

    get_handle: function(element) {
        return MochiKit.Selector.findChildElements(
            element, ['> .block-inner > .edit > .dragger'])[0];
    },

    on_update: function(element) {
        var self = this;
        var d = arguments.callee.$.on_update.call(self);
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self.editor, 'reload');
        });
        return d;
    },
});


zeit.content.cp.TeaserBarContentsSorter = gocept.Class.extend({
    
    __name__: 'zeit.content.cp.TeaserBarSorter',

    construct: function() {
        var self = this;
        new zeit.content.cp.in_context.Editor(self);
        self.sorters = [];
    },

    connect: function() {
        var self = this;
        forEach($$('.block.type-teaser-bar > .block-inner'), function(bar) {
            if (!bar.id) {
                bar.id = bar.parentNode.id + '-inner';
            }
            var url = bar.parentNode.getAttribute(
                'cms:url') + '/@@updateOrder';
            var sorter = new zeit.content.cp.BlockSorter(
                bar.id, {
                constraint: 'horizontal',
                overlap: 'horizontal',
                update_url: url,
            });
            self.sorters.push(sorter);
        });
    },

    disconnect: function() {
        var self = this;
        while (self.sorters.length) {
            var sorter = self.sorters.pop()
            log("Destroying sorter " + sorter.container);
            sorter.__context__.deactivate();
            sorter.__context__.destroy();
        }
    },
    
});


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.content.cp.lead_sorter = new zeit.content.cp.BlockSorter(
        'cp-aufmacher-inner');
    zeit.content.cp.informatives_sorter = new zeit.content.cp.BlockSorter(
        'cp-informatives-inner');
    zeit.content.cp.teaser_bar_sorter = new zeit.content.cp.BlockSorter(
        'cp-teasermosaic');
    zeit.content.cp.teaser_bar_contents_sorter = 
        new zeit.content.cp.TeaserBarContentsSorter();
});


zeit.content.cp.LightBoxForm = zeit.cms.LightboxForm.extend({

    __name__: 'zeit.content.cp.LightBoxForm',

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
            var errors = MochiKit.DOM.getFirstElementByTagAndClassName(
                'ul', 'errors', self.form);
            if (isNull(errors)) {
                self.close();
            }
            return result;
        });
    },

    on_close: function() {
        var self = this;
        log("closing lightbox");
        MochiKit.Signal.disconnect(self.close_event_handle);
        MochiKit.Signal.signal(self, 'before-close');
        MochiKit.Signal.signal(self.parent, 'reload');
    },
});


zeit.content.cp.TabbedLightBoxForm = zeit.content.cp.LightBoxForm.extend({

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        if (!isUndefinedOrNull(self.tabs)) {
            self.tabs.active_tab.activate();
            return
        }
        var tab_definitions = MochiKit.DOM.getElementsByTagAndClassName(
                null, 'lightbox-tab-data', self.context_element.parentNode);
        var i = 0;
        self.tabs = new zeit.cms.Tabs(
                MochiKit.DOM.getFirstElementByTagAndClassName(
                    null, 'lightbox'));
        forEach(tab_definitions, function(tab_definition) {
            var tab_id = 'tab-'+i;
            var tab_view = new zeit.cms.View(
                    tab_definition.href, tab_id);
            var tab = new zeit.cms.ViewTab(
                tab_id, tab_definition.title, tab_view);
            self.tabs.add(tab);
            MochiKit.Signal.connect(tab_view, 'load', function() {
                form = MochiKit.DOM.getFirstElementByTagAndClassName(
                    'form', null, $(tab_view.target_id));
                zeit.content.cp.editor.current_module.rewire_submit_buttons(
                    form);
                $(tab_view.target_id).__handler__ = self;
                self.eval_javascript_tags();
            });
            if (self.context_element == tab_definition) {
                self.tabs.activate(tab_id);
            }
            i = i + 1;
        });
    },

});


zeit.content.cp.LoadAndReload = gocept.Class.extend({

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        var d = zeit.content.cp.makeJSONRequest(url, {});
        return d;
    },

});


zeit.content.cp.AddHighlight = gocept.Class.extend({

    construct: function() {
        var self = this;
        MochiKit.Signal.connect(
            zeit.content.cp.editor, 'added', self, self.added);
    },

});


(function() {

    var added = function(id) {
        log('Added ' + id + $(id));
        MochiKit.Style.setOpacity($(id), 0.0);
        MochiKit.Visual.appear(id);
        MochiKit.Async.callLater(2, function() {
            $(id).style['opacity'] = 1;
        });
    };

    var deleted  = function(id) {
        log('Deleted ' + id + $(id));
        MochiKit.Visual.fade(id, {duration: 0.5,
                                  to: 0.01});
    };

    var ident = MochiKit.Signal.connect(
        window, 'cp-editor-initialized',
        function() {
            MochiKit.Signal.disconnect(ident);
            MochiKit.Signal.connect(
                zeit.content.cp.editor, 'added', added);
            MochiKit.Signal.connect(
                zeit.content.cp.editor, 'deleted', deleted);
    });
})();


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


zeit.content.cp.makeBoxesEquallyHigh = function(container) {
    // check for unloaded images:
    
    var images = MochiKit.DOM.getElementsByTagAndClassName(
        'img', null, container);
    var exit = false;
    forEach(images, function(image) {
        if (!image.height) {
            exit = true;
            throw MochiKit.Iter.StopIteration;
        }
    });
    if (exit) {
        log("Unloaded image in container.id.");
        MochiKit.Async.callLater(
            0.25, zeit.content.cp.makeBoxesEquallyHigh, container);
        return
    }


    var max_height = 0;
    var blocks = [];
    forEach($(container).childNodes, function(block) {
        if (block.nodeType != block.ELEMENT_NODE)
            return
        if (!MochiKit.DOM.hasElementClass(block, 'block'))
            return
        var block = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'block-inner', block);
        if (isNull(block))
            return
        blocks.push(block);
        var height = MochiKit.Style.getStyle(block, 'height');
        MochiKit.Style.setStyle(block, {'height': 'auto'});
        var dim = MochiKit.Style.getElementDimensions(block, true);
        MochiKit.Style.setStyle(block, {'height': height});
        max_height = Math.max(max_height, dim.h);
    }); 

    log("Max height: " + max_height);
    log("Nodes " + blocks);
    forEach(blocks, function(block) {
        var new_dim = new MochiKit.Style.Dimensions(null, max_height)
        MochiKit.Style.setElementDimensions(block, new_dim);
    });
};


(function() {
    
    var fix_box_heights = function() {
        forEach($$('#cp-teasermosaic > .block.type-teaser-bar > .block-inner'),
            function(bar) {
                log("Setting heights for " + bar.parentNode.id);
                try {
                    zeit.content.cp.makeBoxesEquallyHigh(bar);
                } catch (e) {
                    log(e)
                }
        });
    }

    var ident = MochiKit.Signal.connect(
        window, 'cp-editor-initialized',
        function() {
            MochiKit.Signal.disconnect(ident);
            MochiKit.Signal.connect(
                zeit.content.cp.editor, 'after-reload', fix_box_heights);
        });
})();


zeit.content.cp.BusyIndicator = gocept.Class.extend({

    construct: function() {
        var self = this;
        MochiKit.Signal.connect(
            zeit.content.cp.editor, 'busy', self, self.busy_after_a_while)
        MochiKit.Signal.connect(
            zeit.content.cp.editor, 'idle', self, self.idle)
        self.delayer = null; 
        self.indicator = DIV({
            class: 'hidden',
            id: 'busy-indicator'},
            DIV({class: 'shade'}),
            IMG({src: application_url + '/@@/zeit.imp/loading.gif'})
            );
        $('content').appendChild(self.indicator);
    },

    busy_after_a_while: function() {
        var self = this;
        self.delayer = MochiKit.Async.callLater(1, function() {
            self.busy();
        });
    },

    busy: function() {
        var self = this;
        MochiKit.Style.setOpacity(self.indicator, 0);
        MochiKit.DOM.removeElementClass(self.indicator, 'hidden');
        MochiKit.Visual.appear(self.indicator);
    },

    idle: function() {
        var self = this;
        if (!isNull(self.delayer)) {
            self.delayer.cancel();
            self.delayer = null;
        }
        MochiKit.DOM.addElementClass(self.indicator, 'hidden');
    },

});


(function() {
    var ident = MochiKit.Signal.connect(
        window, 'cp-editor-initialized',
        function() {
            MochiKit.Signal.disconnect(ident);
            zeit.content.cp.busy_indicator =
                new zeit.content.cp.BusyIndicator();
        });
})();

