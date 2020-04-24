(function($) {
"use strict";

var nbsp = ' ';

zeit.cms.declare_namespace('zeit.wochenmarkt');

zeit.wochenmarkt.Widget = gocept.Class.extend({

    construct: function(id) {
        var self = this;
        self.id = id;
        self.element = document.getElementById(id + '.wrapper');
        self.list = document.getElementById(id + '.list');
        self.data = document.getElementById(id);
        self.autocomplete = document.getElementById(id + '.add');
        self._initialize_autocomplete();
        self._initialize_sortable();
    },

    _initialize_autocomplete: function() {
        try {
        var self = this;
        $(self.autocomplete).autocomplete({
            source: self.autocomplete.getAttribute('cms:autocomplete-source'),
            minLength: 3,
            focus: function(event, ui) {
                $(self.autocomplete).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                self.add(ui.item.value, ui.item.label, /*pinned=*/true,
                         /*position=*/'start');
                $(self.autocomplete).val('');
                return false;
            },
            appendTo: self.element
        });
        } catch(e) {
            console.log(e);
        }
    },

    _initialize_sortable: function() {
        var self = this;
        $(self.list).sortable({
            items: '> li',
            axis: 'y',
            scroll: false,
            update: function(event, ui) {
                self._sync_json_widget_value();
                $(self.data).trigger('change');
            }
        });
    },

    handle_click: function(event) {
        var self = this;
        var method = event.target().getAttribute('cms:call');
        if (isNull(method)) {
            return;
        }

        method = self[method];
        method.call(self, event);
        event.stop();
    },

    to_json: function() {
        var self = this;
        var result = [];
        $('> li', self.list).each(function(i, el) {
            el = $(el);
            result.push({id: el.attr('cms:uniqueId'),
                         amount: '1'
            });
        });
        return result;
    },

    delete: function(event) {
        var self = this;
        $(event.target()).closest('li').remove();
        self._sync_json_widget_value();
        $(self.data).trigger('change');
    },

    add: function(code, label, pinned, position) {
        var self = this;
        self._add(code, label, pinned, position);
        self._sync_json_widget_value();
    },

    _add: function(code, label, pinned, position) {
        var self = this;
        if (isUndefined(position)) {
            position = 'end';
        }
        var pinned = pinned ? 'pinned' : 'toggle-pin';
        var item = LI(
            {'cms:uniqueId': code},
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}),
            SPAN({'class': 'icon ' + pinned, 'cms:call': 'toggle_pinned'}),
            A({}, label)
        );
        if (position === 'end') {
            $(self.list).append(item);
        } else {
            $(self.list).prepend(item);
        }
    },

    _sync_json_widget_value: function() {
        var self = this;
        $(self.data).val(JSON.stringify(self.to_json()));
        $(self.list).css('width', $(self.list).width() + 'px');
    }

});

})(jQuery);
