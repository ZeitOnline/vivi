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
        self.populate_ingredients($.parseJSON($(self.data).val()));
        MochiKit.Signal.connect(
            id + '.wrapper', 'onclick', self, self.handle_click);
        self._initialize_autocomplete();
        self._initialize_sortable();
        self.element.addEventListener("change", function() { self.update_entry(self.data) } );
    },

    _initialize_autocomplete: function() {
        var self = this;
        $(self.autocomplete).autocomplete({
            source: self.autocomplete.getAttribute('cms:autocomplete-source'),
            minLength: 3,
            focus: function(event, ui) {
                $(self.autocomplete).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                self.add(
                    ui.item.value, ui.item.label,
                    0, /*amount*/
                    '', /*unit*/
                    'start' /*position=*/
                );
                $(self.autocomplete).val('');
                return false;
            },
            appendTo: self.element
        });
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
        self.list.querySelectorAll('.ingredient__amount').forEach(function(i) {
            i.value = i.parentNode.getAttribute('data-amount');
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
            result.push({
                code: el.attr('cms:uniqueId'),
                label: el.text(),
                amount: el.attr('data-amount'),
                unit: el.attr('data-unit')
            });
        });
        return result;
    },

    update_entry: function(data) {
        const id = event.target.parentElement.getAttribute('cms:uniqueid');
        let ingredients = JSON.parse(data.value);
        ingredients.forEach(function(i) {
            if (i.code === id) {
                i.amount = event.target.value;
            };
        });
        data.value = JSON.stringify(ingredients);
    },

    delete: function(event) {
        var self = this;
        $(event.target()).closest('li').remove();
        self._sync_json_widget_value();
        $(self.data).trigger('change');
    },

    add: function(code, label, amount, unit, position) {
        var self = this;
        self._add(code, label, amount, unit, position);
        self._sync_json_widget_value();
    },

    _add: function(code, label, amount, unit, position) {
        var self = this;
        if (isUndefined(position)) {
            position = 'end';
        }
        var item = LI(
            {'cms:uniqueId': code, 'data-amount': amount, 'data-unit': unit},
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}),
            A({}, label),
            INPUT({'id': self.id + '.ingredient__amount', 'class': 'ingredient__amount'}),
        );
        if (position === 'end') {
            $(self.list).append(item);
        } else {
            $(self.list).prepend(item);
        }
    },

    populate_ingredients: function(tags) {
        var self = this;
        $.each(tags, function(i, tag) {
            self._add(tag.code, tag.label, tag.amount, tag.unit);
        });
        self._sync_json_widget_value();
    },

    _sync_json_widget_value: function() {
        var self = this;
        $(self.data).val(JSON.stringify(self.to_json()));
    }

});

})(jQuery);
