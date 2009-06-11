var date_format = '%Y-%m-%d %H:%M';

// Calendar, includes Date object patches for parsing/printing in a
// strptime/strftime like manner
Import(FCKConfig.PageConfig.ApplicationURL +
       '/@@/zc.datetimewidget/calendar.js');
Import(FCKConfig.PageConfig.ApplicationURL +
       '/@@/zc.datetimewidget/lang/calendar-en.js');

zeit.wysiwyg.VideoDialog = zeit.wysiwyg.Dialog.extend({

    construct: function() {
        var self = this;
        self.container_class = $('kind').value;
        arguments.callee.$.construct.call(self);

        self._connect_date_buttons();

        var id = self.container_class + 'Id';
        $('avid').value = self.get_value(id);
        $('expires').value = self.get_value('expires');
        $('format').value = self.get_value('format');
    },

    _connect_date_buttons: function() {
        MochiKit.Signal.connect($('expires.1w'), 'onclick', function(event) {
            var date = new Date();
            date.setDate(date.getDate() + 5);
            $('expires').value = date.print(date_format);
        });

        MochiKit.Signal.connect($('expires.1m'), 'onclick', function(event) {
            var date = new Date();
            date.setDate(date.getDate() + 30);
            $('expires').value = date.print(date_format);
        });

        MochiKit.Signal.connect($('expires.infty'), 'onclick', function(event) {
            $('expires').value = '';
        });
    },

    validate: function() {
        var self = this;
        if (! $('avid').value) {
            $('avid').focus();
            alert('Die ID muss ausgefüllt werden.');
            return false;
        }
        var expires = $('expires').value;
        if (expires) {
            // Make sure date is valid and matches format
            if (Date.parseDate(expires, date_format).print(date_format)
                != expires) {
                alert('Das Datumsformat stimmt nicht: ' + date_format);
                $('expires').focus();
                return false;
            }
        }
        return true;
    },

    update: function() {
        var self = this;
        var id = self.container_class + 'Id';
        self.set_value(id, $('avid').value);
        self.set_value('expires', $('expires').value);
        self.set_value('format', $('format').value);
    },

    create: function() {
        var self = this;
        var div = DIV({'class': self.container_class},
            DIV({'class': self.container_class + 'Id'}),
            DIV({'class': 'expires'}),
            DIV({'class': 'format'}));
        self.create_element(div);
        return div;
    },
});


zeit.wysiwyg.dialog_class = zeit.wysiwyg.VideoDialog;
