
zeit.cms.declare_namespace('zeit.content.cp');

zeit.cms.in_cp_editor = function() {
    return Boolean(jQuery('.cp-editor-inner').length);
};

zeit.content.cp.LoadAndReloadWithConfirm = zeit.edit.LoadAndReload.extend({
    construct: function(context_element) {
        var self = this;
        if (confirm('Wirklich löschen?')) {
            arguments.callee.$.construct.call(self, context_element);
        }
    }
});

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

MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (! zeit.cms.in_cp_editor()) {
        return;
    }
    zeit.content.cp.block_hover = new zeit.content.cp.BlockHover();
});


zeit.content.cp.ContainerMover = gocept.Class.extend({

    construct: function(container_type) {
        var self = this;
        self.movers = [];
        self.container_type = container_type;
        self.selector = '.type-' + container_type;
        self.__name__ = ('zeit.content.cp.ContainerMover('
            + self.container_type + ')');
        new zeit.edit.context.Editor(self);
    },

    connect: function() {
        var self = this;
        jQuery(self.selector).each(function() {
            var mover = new zeit.edit.sortable.BlockMover(
                this.id, '#' + this.id + ' > div.block-inner');
            mover.__name__ = ('zeit.content.cp.BlockMover('
                + self.container_type + ', id=' + this.id + ')');
            self.movers.push(mover);
        });
    },

    disconnect: function() {
        var self = this;
        while (self.movers.length) {
            var mover = self.movers.pop();
            log("Destroying mover " + mover.container);
            mover.__context__.deactivate();
            mover.__context__.destroy();
        }
    }

});


var ident = MochiKit.Signal.connect(
    window, 'script-loading-finished', function() {
    MochiKit.Signal.disconnect(ident);
    if (! zeit.cms.in_cp_editor()) {
        return;
    }

    zeit.content.cp.body_mover = new zeit.edit.sortable.BlockSorter(
        'body', '#body');
    zeit.content.cp.body_mover.__name__ = (
        'zeit.content.cp.ContainerMover(body)');

    zeit.content.cp.region_mover = new zeit.content.cp.ContainerMover(
        'region');
    zeit.content.cp.area_mover = new zeit.content.cp.ContainerMover('area');
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
