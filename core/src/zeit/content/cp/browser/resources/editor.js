
zeit.cms.declare_namespace('zeit.content.cp');

zeit.content.cp.getParentComponent = function(context_element) {
    var parent = null;
    var parent_element = context_element.parentNode;
    while (!isNull(parent_element) && isUndefinedOrNull(parent)) {
        parent = parent_element.__handler__;
        parent_element = parent_element.parentNode;
    }
    return parent;
}




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



zeit.content.cp.TeaserBarContentsSorter = gocept.Class.extend({
    
    __name__: 'zeit.content.cp.TeaserBarSorter',

    construct: function() {
        var self = this;
        new zeit.edit.context.Editor(self);
        self.sorters = [];
    },

    connect: function() {
        var self = this;
        forEach($$('.block.type-teaser-bar > .block-inner'), function(bar) {
            if (!bar.id) {
                bar.id = bar.parentNode.id + '-inner';
            }
            var url = bar.parentNode.getAttribute(
                'cms:url');
            var sorter = new zeit.edit.sortable.BlockSorter(
                bar.id, {
                constraint: 'horizontal',
                overlap: 'horizontal',
                update_url: url + '/@@updateOrder',
                reload_id: bar.parentNode.id,
                reload_url: url + '/@@contents',
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
    zeit.content.cp.lead_sorter = new zeit.edit.sortable.BlockSorter(
        'lead');
    zeit.content.cp.informatives_sorter = new zeit.edit.sortable.BlockSorter(
        'informatives');
    zeit.content.cp.teaser_bar_sorter = new zeit.edit.sortable.BlockSorter(
        'teaser-mosaic');
    zeit.content.cp.teaser_bar_contents_sorter = 
        new zeit.content.cp.TeaserBarContentsSorter();
});


zeit.content.cp.LightBoxForm = zeit.cms.LightboxForm.extend({

    __name__: 'zeit.content.cp.LightBoxForm',
    context: zeit.edit.context.Lightbox,

    construct: function(context_element) {
        var self = this;
        self.context_element = context_element;
        var container_id = context_element.getAttribute('cms:lightbox-in');
        self.parent = zeit.content.cp.getParentComponent(context_element);
        var url = context_element.getAttribute('href');
        self.reload_id = context_element.getAttribute(
            'cms:lightbox-reload-id');
        self.reload_url = context_element.getAttribute(
            'cms:lightbox-reload-url');
        arguments.callee.$.construct.call(self, url, $(container_id));
        self.lightbox.content_box.__handler__ = self;
        self.reload_parent_component_on_close = true;
        new self.context(self);
    },

    connect: function() {
        var self = this;
        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'before-reload', function() {
                self.reload_parent_component_on_close = false;
                self.close();
        }));
        self.close_event_handle = MochiKit.Signal.connect(
            self.lightbox, 'before-close',
            self, self.on_close);
        self.events.push(
            MochiKit.Signal.connect(
                self, 'reload', self, self.reload));
    },

    disconnect: function() {
        // hum, do we need to do anything here? We use the lightbox events
        // right now.
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        var d = arguments.callee.$.reload.call(self);
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self, 'after-reload');
            return result;
        });
        return d;
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
        if (self.reload_parent_component_on_close) {
            MochiKit.Signal.signal(
                self.parent, 'reload',
                self.reload_id, self.reload_url);
        }
    },
});


zeit.content.cp.TabbedLightBoxForm = zeit.content.cp.LightBoxForm.extend({

    __name__: 'zeit.content.cp.TabbedLightBoxForm',

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        if (!isUndefinedOrNull(self.tabs)) {
            self.tabs.active_tab.view.render();
            return
        }
        var tab_definitions = MochiKit.DOM.getElementsByTagAndClassName(
                null, 'lightbox-tab-data', self.context_element.parentNode);
        var i = 0;
        self.tabs = new zeit.cms.Tabs(
                self.lightbox.content_box);
        forEach(tab_definitions, function(tab_definition) {
            var tab_id = 'tab-'+i;
            var tab_view = new zeit.cms.View(
                    tab_definition.href, tab_id);
            var tab = new zeit.cms.ViewTab(
                tab_id, tab_definition.title, tab_view);
            self.tabs.add(tab);
            self.events.push(
                MochiKit.Signal.connect(
                    tab_view, 'load', function() {
                    var form = MochiKit.DOM.getFirstElementByTagAndClassName(
                        'form', null, $(tab_view.target_id));
                    if (!isNull(form)) {
                        self.rewire_submit_buttons(form);
                    }
                    $(tab_view.target_id).__handler__ = self;
                    self.eval_javascript_tags();
                    MochiKit.Signal.signal(self, 'after-reload')
            }));
            if (self.context_element == tab_definition) {
                self.tabs.activate(tab_id);
            }
            i = i + 1;
        });
    },

});


(function() {

    var added = function(id) {
        log('added');
        log('added ' + id);
        if (isNull($(id))) {
            log("Added but not found: " + id);
            return
        }
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
                zeit.edit.editor, 'added', added);
            MochiKit.Signal.connect(
                zeit.edit.editor, 'deleted', deleted);
    });
})();


zeit.content.cp.makeBoxesEquallyHigh = function(container) {
    // check for unloaded images:
    
    log("fixing box heights.", container.id);
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

    forEach(blocks, function(block) {
        var new_dim = new MochiKit.Style.Dimensions(null, max_height)
        MochiKit.Style.setElementDimensions(block, new_dim);
    });
};


(function() {
    
    var fix_box_heights = function() {
        log('fixing box heights');
        forEach($$('#teaser-mosaic > .block.type-teaser-bar > .block-inner'),
            function(bar) {
                log('fixing box heights for', bar.id);
                try {
                    zeit.content.cp.makeBoxesEquallyHigh(bar);
                } catch (e) {
                    log("Error", e)
                }
        });
    }

    var ident = MochiKit.Signal.connect(
        window, 'cp-editor-initialized',
        function() {
            MochiKit.Signal.disconnect(ident);
            MochiKit.Signal.connect(
                zeit.edit.editor, 'after-reload', fix_box_heights);
        });
})();

