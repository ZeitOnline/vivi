if (isUndefinedOrNull(zeit.content)) {
    zeit.content = {}
}
zeit.content.cp = {}

zeit.content.cp.Editor = Class.extend({
    
    construct: function() {
        var self = this;
        MochiKit.Signal.connect(
            'cp-content', 'onclick',
            self, 'handleContentClick');
        self.edit_pane = $('cp-edit-pane');
        self.connect_draggables();
    },

    handleContentClick: function(event) {
        var self = this;
        var module_name = event.target().getAttribute('cms:cp-module')
        log("Loading module " + module_name);
        if (!module_name) {
            return
        }
        event.stop();
        var module = zeit.content.cp.modules[module_name]
        new module(event.target());
    },
    
    connect_draggables: function() {
        var self = this;
        MochiKit.Sortable.create($('cp-content'), {
            constraint: null,
            only: ['box'],
            tag: 'div',
            tree: true,
        });
        /*var boxes = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'box', $('cp-content'));
        forEach(boxes, function(box) {
            new MochiKit.DragAndDrop.Draggable(box);
        });
        */
    },
});


zeit.content.cp.BoxHover = Class.extend({

    construct: function() {
        var self = this;
        // doesn't look good, yet
        return
        MochiKit.Signal.connect('cp-content', 'onmouseover', self, 'over');
        MochiKit.Signal.connect('cp-content', 'onmouseout', self, 'out');
    },

    over: function(event) {
        MochiKit.DOM.addElementClass(event.target(), 'hover');
    },

    out: function(event) {
        MochiKit.DOM.removeElementClass(event.target(), 'hover');
    },
});

MochiKit.Signal.connect(window, 'onload', function() {
    if (isNull($('cp-content'))) {
        return
    }
    document.cpeditor = new zeit.content.cp.Editor();
    new zeit.content.cp.BoxHover();
});


/* modules */
zeit.content.cp.modules = {}

zeit.content.cp.modules.LightBoxForm = Class.extend({

    construct: function(context_element) {
        var self = this;
        self.panel_view = context_element.getAttribute('href');
        new zeit.cms.LightboxForm(self.panel_view, $('cp-content'));
    },

});
