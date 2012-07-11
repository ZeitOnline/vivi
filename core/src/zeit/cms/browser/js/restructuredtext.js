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

        // XXX This assumes knowlegde outside the widget about how the form is
        // rendered. Unfortunately there doesn't seem to be another way to
        // achieve a large enough click area.
        self.preview.closest('.field').bind('click', function(event) {
            if (event.target.nodeName == 'A') {
                return;
            }
            self.preview.hide();
            self.textarea.show();
            self.textarea.focus();
        });

        $('a', self.preview).each(function(i, elem) {
            $(elem).attr('target', '_blank');
        });

        if (! self.preview.text()) {
            self.preview.addClass('empty');
        }
    }

});

}(jQuery));