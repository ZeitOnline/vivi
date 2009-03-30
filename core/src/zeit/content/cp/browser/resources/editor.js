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
        var module = zeit.content.cp.modules[module_name]
        new module();
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

zeit.content.cp.modules.BaseModule = Class.extend({

    panel_view: null,
    
    construct: function(context_element) {
        var self = this;
        self.context = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, null, 'editable-area');
        self.load_panel()
    },

    load_panel: function() {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(self.panel_view);
        d.addCallback(function(result) {
            document.cpeditor.edit_pane.innerHTML = result.responseText;
        });
    },

});


zeit.content.cp.modules.AddPanel = zeit.content.cp.modules.BaseModule.extend({

    panel_view: 'editor.add-panel',    

});

