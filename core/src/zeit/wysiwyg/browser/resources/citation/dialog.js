zeit.wysiwyg.CitationDialog = zeit.wysiwyg.Dialog.extend({

    construct: function() {
        var self = this;
        self.container_class = 'citation';
        arguments.callee.$.construct.call(self);
        self.attributes = ['text', 'attribution',
                           'text2', 'attribution2', 'layout'];
        MochiKit.Iter.forEach(self.attributes, function(attribute) {
            $(attribute).value = self.get_value(attribute);
        });
    },

    update: function() {
        var self = this;
        MochiKit.Iter.forEach(self.attributes, function(attribute) {
            self.set_value(attribute, $(attribute).value);
        });
    },

    create: function() {
        var self = this;
        var children = [];
        MochiKit.Iter.forEach(self.attributes, function(attribute) {
            children.push(DIV({'class': attribute}));
        });
        var div = DIV({'class': 'inline-element ' + self.container_class},
            children);
        self.create_element(div);
        return div;
    },
});


zeit.wysiwyg.dialog_class = zeit.wysiwyg.CitationDialog;
