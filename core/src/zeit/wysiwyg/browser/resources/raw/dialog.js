zeit.wysiwyg.RawDialog = zeit.wysiwyg.Dialog.extend({

    construct: function() {
        var self = this;
        self.container_class = 'raw';
        arguments.callee.$.construct.call(self);
        if (self.container === null)
            return;
        $('raw').value = self.container.textContent;
    },

    update: function() {
        var self = this;
        self.container.textContent = $('raw').value;
    },

    create: function() {
        var self = this;
        var div = DIV({'class': 'inline-element ' + self.container_class});
        self.create_element(div);
        return div;
    },
});


zeit.wysiwyg.dialog_class = zeit.wysiwyg.RawDialog;
