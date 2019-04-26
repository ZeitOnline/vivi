zeit.wysiwyg.PageBreakDialog = zeit.wysiwyg.Dialog.extend({

    construct: function() {
        var self = this;
        self.container_class = 'page-break';
        arguments.callee.$.construct.call(self);
        $('teaser').value = self.get_value('teaser');
    },

    update: function() {
        var self = this;
        self.set_value('teaser', $('teaser').value);
    },

    create: function() {
        var self = this;
        var div = DIV({'class': 'inline-element ' + self.container_class},
            DIV({'class': 'teaser'}));
        self.create_element(div);
        return div;
    },
});


zeit.wysiwyg.dialog_class = zeit.wysiwyg.PageBreakDialog;
