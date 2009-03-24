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
        self.edit_pane.innerHTML = event.target().id;

    },
    
    connect_draggables: function() {
        var self = this;
        MochiKit.Sortable.create($('cp-content'), {
            constraint: null,
            overlap: null,
            only: ['box', 'editable-area'],
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
        // add handlers which highlight hovered, editable elements
    },
});

MochiKit.Signal.connect(window, 'onload', function() {
    if (isNull($('cp-content'))) {
        return
    }
    document.cpeditor = new zeit.content.cp.Editor();
    new zeit.content.cp.BoxHover();
});
