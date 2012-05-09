// Copyright (c) 2012 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {


zeit.cms.RestructuredTextWidget = gocept.Class.extend({

    construct: function(widget_id) {
        var self = this;
        widget_id = widget_id.replace('.', '\\.');
        self.textarea = $('#' + widget_id);
        self.preview = $('#' + widget_id + '\\.preview');
        self.textarea.hide();

        self.preview.bind('click', function(event) {
            if (event.target.nodeName == 'A') {
                return;
            }
            self.preview.hide();
            self.textarea.show();
            self.textarea.focus();
        });
    }

});

}(jQuery));