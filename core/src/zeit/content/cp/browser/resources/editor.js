
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


zeit.content.cp.ContainerSorter = gocept.Class.extend({

    construct: function(container_type) {
        var self = this;
        self.sorters = [];
        self.container_type = container_type;
        self.selector = '.type-' + container_type;
        self.__name__ = ('zeit.content.cp.ContainerSorter('
            + self.container_type + ')');
        new zeit.edit.context.Editor(self);
    },

    connect: function() {
        var self = this;
        jQuery(self.selector).each(function() {
            var sorter = new zeit.edit.sortable.BlockSorter(
                this.id, '#' + this.id + ' > div.block-inner');
            sorter.__name__ = ('zeit.content.cp.BlockSorter('
                + self.container_type + ', id=' + this.id + ')');
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

    zeit.content.cp.body_sorter = new zeit.edit.sortable.BlockSorter(
        'body', '#body > div.block-inner');
    zeit.content.cp.body_sorter.__name__ = (
        'zeit.content.cp.ContainerSorter(body)');

    zeit.content.cp.region_sorter = new zeit.content.cp.ContainerSorter(
        'region');
    zeit.content.cp.area_sorter = new zeit.content.cp.ContainerSorter('area');
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
