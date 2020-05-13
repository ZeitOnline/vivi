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
                    '', /*amount*/
                    'Stück', /*unit*/
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
        self.list.querySelectorAll('[data-name = "ingredient__item"]').forEach(function(i) {
            i.querySelector('input').value = i.getAttribute('data-amount');
            i.querySelector('select').value = i.getAttribute('data-unit');
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
                label: el.contents().get(1).text,
                amount: el.attr('data-amount'),
                unit: el.attr('data-unit')
            });
        });
        return result;
    },

    update_entry: function(data) {
        const parent_el = event.target.parentElement;
        const id = parent_el.getAttribute('cms:uniqueid');
        let ingredients = JSON.parse(data.value);
        ingredients.forEach(function(i) {
            if (i.code === id) {
                const val = event.target.value;
                if (event.target.getAttribute('data-id') === 'amount' && isNaN(parseInt(val))) {
                    event.target.style.background = 'linear-gradient(0deg, #FFF, #FDD)';
                } else {
                    i[event.target.getAttribute('data-id')] = val;
                    event.target.style.background = 'linear-gradient(0deg, #FFF, #CFD)';
                }
            }
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
            {'class': 'ingredient__item', 'cms:uniqueId': code, 'data-amount': amount, 'data-unit': unit, 'data-name': 'ingredient__item'},
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}),
            A({'class': 'ingredient__label'}, label),
            INPUT({'id': self.id + '.ingredient__amount', 'class': 'ingredient__amount', 'data-id': 'amount'}),
        );
        let select = SELECT({'class': 'ingredient__unit', 'data-id': 'unit'});
        ['Stück', 'kg', 'g', 'l', 'ml'].forEach(function(i) {
            select.appendChild(OPTION({}, i));
        });
        item.appendChild(select);
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
