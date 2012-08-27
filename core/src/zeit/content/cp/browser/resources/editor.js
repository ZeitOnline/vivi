
zeit.cms.declare_namespace('zeit.content.cp');

zeit.cms.in_cp_editor = function() {
    return Boolean(jQuery('.cp-editor-inner').length);
};

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
        var css_class = 'block';
        if (MochiKit.DOM.hasElementClass(element, css_class)) {
            return element;
        }
        return MochiKit.DOM.getFirstParentByTagAndClassName(
            element, null, css_class);
    }
});

MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    if (! zeit.cms.in_cp_editor()) {
        return;
    }
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
                reload_url: url + '/@@contents'
            });
            self.sorters.push(sorter);
        });
    },

    disconnect: function() {
        var self = this;
        while (self.sorters.length) {
            var sorter = self.sorters.pop();
            log("Destroying sorter " + sorter.container);
            sorter.__context__.deactivate();
            sorter.__context__.destroy();
        }
    }

});


MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    if (! zeit.cms.in_cp_editor()) {
        return;
    }
    zeit.content.cp.lead_sorter = new zeit.edit.sortable.BlockSorter(
        'lead');
    zeit.content.cp.informatives_sorter = new zeit.edit.sortable.BlockSorter(
        'informatives');
    zeit.content.cp.teaser_bar_sorter = new zeit.edit.sortable.BlockSorter(
        'teaser-mosaic');
    zeit.content.cp.teaser_bar_contents_sorter =
        new zeit.content.cp.TeaserBarContentsSorter();
});



(function() {

    var added = function(id) {
        log('added');
        log('added ' + id);
        if (isNull($(id))) {
            log("Added but not found: " + id);
            return;
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
        window, 'script-loading-finished', function() {
            MochiKit.Signal.disconnect(ident);
            if (! zeit.cms.in_cp_editor()) {
                return;
            }
            MochiKit.Signal.connect(zeit.edit.editor, 'added', added);
            MochiKit.Signal.connect(zeit.edit.editor, 'deleted', deleted);
    });
}());


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
        return;
    }

    var max_height = 0;
    var blocks = [];
    forEach($(container).childNodes, function(block) {
        if (block.nodeType != block.ELEMENT_NODE) {
            return;
        }
        if (!MochiKit.DOM.hasElementClass(block, 'block')) {
            return;
        }
        var block_inner = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'block-inner', block);
        if (isNull(block)) {
            return;
        }
        blocks.push(block_inner);
        var height = MochiKit.Style.getStyle(block_inner, 'height');
        MochiKit.Style.setStyle(block_inner, {'height': 'auto'});
        var dim = MochiKit.Style.getElementDimensions(block_inner, true);
        MochiKit.Style.setStyle(block_inner, {'height': height});
        max_height = Math.max(max_height, dim.h);
    });

    forEach(blocks, function(block) {
        var new_dim = new MochiKit.Style.Dimensions(null, max_height);
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
                    log("Error", e);
                }
        });
    };

    var ident = MochiKit.Signal.connect(
        window, 'script-loading-finished', function() {
            MochiKit.Signal.disconnect(ident);
            if (! zeit.cms.in_cp_editor()) {
                return;
            }
            MochiKit.Signal.connect(
                zeit.edit.editor, 'after-reload', fix_box_heights);
        });
}());
