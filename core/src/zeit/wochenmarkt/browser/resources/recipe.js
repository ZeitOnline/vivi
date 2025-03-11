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
        units = JSON.parse(result.response);
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
        self.element.addEventListener("change", function(event) { self.update_entry(event); } );
        self.validate_recipe_title();
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
                    ''  /*details*/
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
                unique_id: el.attr('data-id'),
                code: el.attr('data-code'),
                label: el.contents().get(0).text,
                amount: el.attr('data-amount'),
                unit: el.attr('data-unit'),
                details: el.attr('data-details')
            });
        });
        return result;
    },

    update_entry: function(event) {
        var self = this;
        const input = event.target;
        const li = input.parentElement;
        const name = input.getAttribute('data-id');
        const value = input.value;
        input.classList.add('dirty');
        // amount either needs to be a number or empty.
        if (name === 'amount' && (isNaN(Number(value)) && value !== '')) {
            input.style.background = 'linear-gradient(0deg, #FFF, #FDD)';
        } else {
            input.style.background = 'linear-gradient(0deg, #FFF, #CEF)';
            li.setAttribute('data-' + name, value);
        }
        self._sync_json_widget_value();
    },

    validate_recipe_title: function() {
        // It's just a simple notification that does not prevent the article
        // form being edited, checked in or published.
        const title_id = this.id.replace('.ingredients', '.title');
        const title = document.getElementById(title_id);
        if (title.value === "") {
            title.closest('.fieldname-title').classList.add('notification');
        }
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
        // As it is possible to add duplicate ingredients, we cannot rely on the
        // ingredient id (aka code) alone. Thus we add a random number stub,
        // serving as unique id. Since we're dealing only with a relatively
        // small number of ingredients per document, using a simple random
        // function is sufficient.
        //
        // Math.random() always returns something like 0.123..., so for our id,
        // we only want to use the stub from the right side of the comma.
        const unique_id = code + '_' + Math.random().toString().split('.')[1];
        var item = LI(
            {'class': 'ingredient__item', 'data-id': unique_id, 'data-code': code, 'data-amount': amount, 'data-unit': unit, 'data-details': details, 'data-name': 'ingredient__item'},
            A({'class': 'ingredient__label'}, label),
            INPUT({'id': self.id + '.ingredient__amount', 'class': 'ingredient__amount', 'data-id': 'amount', 'placeholder': 'Anzahl'})
        );

        // Add unit
        let select = SELECT({'class': 'ingredient__unit', 'data-id': 'unit'});
        units.forEach(function(u) {
            select.appendChild(OPTION({'value': u.id}, u.title));
        });
        select.value = unit;
        item.appendChild(select);

        // Add details
        const details_input = INPUT({'id': self.id + '.ingredient__details', 'class': 'ingredient__details', 'data-id': 'details', 'size': 1, 'placeholder': 'weitere Angaben'});
        item.appendChild(details_input);

        // Add delete button
        item.appendChild(
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}));

        $(self.list).append(item);
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
                self.add(ui.item.value, ui.item.label);
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
            A({'class': 'recipe-category__label'}, label)
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
