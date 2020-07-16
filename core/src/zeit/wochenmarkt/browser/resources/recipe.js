(function($) {
"use strict";

/*
 * Fetch units through xhr. We want to do this only once during form load, thus
 * it is defined globally here instead of being part of IngredientsWidget, which
 * is reinitialized every time a change to the recipe list has been made.
 */
let units;
setup_units();

function setup_units() {
    const source = zeit.cms.locked_xhr(
        application_url + '/@@source?name=zeit.content.modules.interfaces.RecipeUnitsSource');
    source.addCallback(function(result) {
        units = JSON.parse(result.response)
        return result;
    });
    source.addErrback(function(error) {
        zeit.cms.log_error(error);
        return error;
    });
}

zeit.cms.declare_namespace('zeit.wochenmarkt');

zeit.wochenmarkt.IngredientsWidget = gocept.Class.extend({

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
            minLength: 2,
            focus: function(event, ui) {
                $(self.autocomplete).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                self.add(
                    ui.item.value, ui.item.label,
                    '', /*amount*/
                    '', /*unit*/
                    '', /*details*/
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
            i.querySelector('.ingredient__amount').value = i.getAttribute('data-amount');
            i.querySelector('.ingredient__unit').value = i.getAttribute('data-unit');
            i.querySelector('.ingredient__details').value = i.getAttribute('data-details');
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
                label: el.contents().get(0).text,
                amount: el.attr('data-amount'),
                unit: el.attr('data-unit'),
                details: el.attr('data-details')
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
                // amount either needs to be a number or empty.
                if (event.target.getAttribute('data-id') === 'amount' && (isNaN(Number(val)) && val !== '')) {
                    event.target.style.background = 'linear-gradient(0deg, #FFF, #FDD)';
                    event.target.classList.add('dirty');
                } else {
                    i[event.target.getAttribute('data-id')] = val;
                    event.target.style.background = 'linear-gradient(0deg, #FFF, #CFD)';
                    event.target.classList.add('dirty');
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

    add: function(code, label, amount, unit, details) {
        var self = this;
        self._add(code, label, amount, unit, details);
        self._sync_json_widget_value();
    },

    _add: function(code, label, amount, unit, details) {
        var self = this;
        var item = LI(
            {'class': 'ingredient__item', 'cms:uniqueId': code, 'data-amount': amount, 'data-unit': unit, 'data-details': details, 'data-name': 'ingredient__item'},
            A({'class': 'ingredient__label'}, label),
            INPUT({'id': self.id + '.ingredient__amount', 'class': 'ingredient__amount', 'data-id': 'amount', 'placeholder': 'Anzahl'}),
        );

        // Add unit
        let select = SELECT({'class': 'ingredient__unit', 'data-id': 'unit'});
        self._add_units(select, unit);
        item.appendChild(select);

        // Add details
        const details_input = INPUT({'id': self.id + '.ingredient__details', 'class': 'ingredient__details', 'data-id': 'details', 'size': 1, 'placeholder': 'weitere Angaben'});
        item.appendChild(details_input);

        // Delete button
        item.appendChild(
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}));

        $(self.list).append(item);
    },

    _add_units: function(element, value) {
        units.forEach(function(u) {
            element.appendChild(OPTION({'value': u.id}, u.title));
        });
        element.value = value;
    },

    populate_ingredients: function(ingredients) {
        var self = this;
        $.each(ingredients, function(i, ingredient) {
            self._add(
                ingredient.code,
                ingredient.label,
                ingredient.amount,
                ingredient.unit,
                ingredient.details);
        });
        self._sync_json_widget_value();
    },

    _sync_json_widget_value: function() {
        var self = this;
        $(self.data).val(JSON.stringify(self.to_json()));
    }

});


zeit.wochenmarkt.RecipeCategoriesWidget = gocept.Class.extend({

    construct: function(id) {
        var self = this;
        self.id = id;
        self.element = document.getElementById(id + '.wrapper');
        self.list = document.getElementById(id + '.list');
        self.data = document.getElementById(id);
        self.autocomplete = document.getElementById(id + '.add');
        self.populate_categories($.parseJSON($(self.data).val()));
        MochiKit.Signal.connect(
            id + '.wrapper', 'onclick', self, self.handle_click);
        self._initialize_autocomplete();
        self._initialize_sortable();
    },

    _initialize_autocomplete: function() {
        var self = this;
        $(self.autocomplete).autocomplete({
            source: self.autocomplete.getAttribute('cms:autocomplete-source'),
            minLength: 2,
            focus: function(event, ui) {
                $(self.autocomplete).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                self.add(
                    ui.item.value, ui.item.label,
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

    add: function(code, label) {
        var self = this;
        self._add(code, label);
        self._sync_json_widget_value();
    },

    _add: function(code, label) {
        var self = this;
        var item = LI(
            {'class': 'recipe-category__item', 'cms:uniqueId': code, 'data-name': 'recipe-category__item'},
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}),
            A({'class': 'recipe-category__label'}, label),
        );
        $(self.list).append(item);
    },

    populate_categories: function(tags) {
        var self = this;
        $.each(tags, function(i, tag) {
            self._add(tag.code, tag.label);
        });
        self._sync_json_widget_value();
    },

    _sync_json_widget_value: function() {
        var self = this;
        $(self.data).val(JSON.stringify(self.to_json()));
    }

});

})(jQuery);
