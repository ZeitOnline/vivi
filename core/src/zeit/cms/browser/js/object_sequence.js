// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt


zeit.cms.ObjectSequenceWidget = gocept.Class.extend({

    construct: function(widget_id, accept) {
        var self = this;
        self.widget_id = widget_id;
        self.element = $(widget_id);
        self.ul_element = MochiKit.DOM.getFirstElementByTagAndClassName(
            'ul', null, self.element);

        self.initialize_autocomplete();
        self.initialize();
        // XXX Need to unregister those events
        MochiKit.Signal.connect(
            self.element, 'onclick', self, self.handleClick);
        new MochiKit.DragAndDrop.Droppable(self.element, {
            accept: accept,
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                self.handleDrop(element);
            }
        });
    },

    initialize_autocomplete: function() {
        var self = this;
        self.autocomplete = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', 'autocomplete', self.element);
        if (isNull(self.autocomplete)) {
            return;
        }
        jQuery(self.autocomplete).autocomplete({
            source: self.autocomplete.getAttribute('cms:autocomplete-source'),
            select: function(event, ui) {
                self.add(ui.item.value);
            }
        });
    },

    initialize: function() {
        var self = this;
        MochiKit.Sortable.destroy(self.ul_element);
        self.ul_element.innerHTML = '';
        var i = 0;
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
                'input', 'uniqueId', self.element),
            function(input) {
                MochiKit.DOM.appendChildNodes(
                    self.ul_element,
                    self.renderElement(i, input.value));
                i += 1;
        });
        MochiKit.Sortable.create(
            self.ul_element, {
            onUpdate: function() { self.update_order_from_ul(); }
            });
        if (i == 0 && isNull(self.autocomplete)) {
            self.ul_element.appendChild(LI(
                {'class': 'new'},
                'Ziehen Sie Inhalte hierher um sie zu verknüpfen.'));
            MochiKit.DOM.addElementClass(self.element, 'landing-zone');
            MochiKit.DOM.addElementClass(self.element, 'visible');
        } else {
            MochiKit.DOM.removeElementClass(self.element, 'landing-zone');
            MochiKit.DOM.removeElementClass(self.element, 'visible');
        }
    },

    renderElement: function(index, uniqueId) {
        var self = this;
        var li_id = self.widget_id + '_sort_li_' + index;
        var li = LI({'class': 'element busy', 'index': index, 'id': li_id});
        var d = zeit.cms.load_object_details(uniqueId);
        d.addCallbacks(
            function(result) {
                li.innerHTML = result;
                li.insertBefore(
                    // XXX proper i18n
                    A({href: index, rel: "remove", title: "Entfernen"}),
                    li.firstChild);
                return result;
            },
            function(error) {
                zeit.cms.log_error(error);
                li.innerHTML = "Fehler beim Laden";
                return error;
            });
        d.addBoth(function(result) {
            MochiKit.DOM.removeElementClass(li, 'busy');
            return result;
        });
        return li;
    },

    increaseCount: function() {
        var count_field = this.getCountField();
        var count = Number(count_field.value);
        count_field.value = count + 1;
        return count_field.value;
    },

    decreaseCount: function() {
        var count_field = this.getCountField();
        var count = Number(count_field.value);
        count_field.value = count - 1;
        return count_field.value;
    },

    getCountField: function() {
        return MochiKit.DOM.getElement(this.widget_id + '.count');
    },

    getValueField: function(index) {
        return MochiKit.DOM.getElement(this.getValueFieldName(index));
    },

    getValueFieldName: function(index) {
        var self = this;
        return self.widget_id + '.' + index;
    },

    add: function(value) {
        var self = this;
        var next_id = self.increaseCount() - 1;

        var id_field_name = self.getValueFieldName(next_id);

        MochiKit.DOM.appendChildNodes(
            self.element,
            INPUT({'type': 'hidden',
                   'class': 'uniqueId',
                   'name': id_field_name,
                   'id': id_field_name,
                   'value': value}));
        this.initialize();
        self.changed();
    },

    remove: function(index) {
        var self = this;

        MochiKit.DOM.removeElement(self.getValueField(index));

        var new_index = 0;
        self.iterFields(function(value_field) {
            var value_field_name = self.getValueFieldName(new_index);
            value_field.setAttribute('name', value_field_name);
            value_field.setAttribute('id', value_field_name);
            new_index += 1;
        });
        self.decreaseCount();
        self.initialize();
        self.changed();
    },

    iterFields: function(callable) {
        var othis = this;
        var count_field = this.getCountField();
        var amount = Number(count_field.value);
        forEach(MochiKit.Iter.range(amount), function(iteration_index) {
            var value_field = othis.getValueField(iteration_index);
            if (value_field === null) {
                return;
            }
            callable(value_field);
        });
    },

    handleClick: function(event) {
        var self = this;
        var target = event.target();
        var action;
        var argument;
        if (target.nodeName == 'A' &&
            target.rel) {
            action = target.rel;
            argument = target.getAttribute('href');
        }
        if (action && argument) {
            self[action](argument);
            event.stop();
        }
    },

    handleDrop: function(element) {
        var self = this;
        if (MochiKit.DOM.isChildNode(element, self.ul_element)) {
            return;
        }
        var unique_id = element.uniqueId;
        if (unique_id) {
            self.add.call(self, unique_id);
        }
    },

    changed: function() {
        var self = this;
        MochiKit.Signal.signal(
            self.getCountField(), 'onchange', {target: self.getCountField()});
    },

    update_order_from_ul: function() {
        var self = this;
        var ordered_ids = [];
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
                'li', null, self.ul_element),
            function(li) {
                var index = li.getAttribute('index');
                if (!isUndefinedOrNull(index)) {
                    ordered_ids.push(self.getValueField(index).value);
                }
        });
        var i;
        for (i = 0; i < ordered_ids.length; i++) {
            self.getValueField(i).value = ordered_ids[i];
        }
        self.changed();
    },

    show_add_view: function(add_view) {
        var self = this;
        var url = window.application_url + '/@@' + add_view;
        self.lightbox = new zeit.cms.ObjectAddForm(url, $('body'));
        self.lightbox.events.push(MochiKit.Signal.connect(
            self.lightbox, 'zeit.cms.ObjectReferenceWidget.selected',
            function(uniqueId) {
                self.add(uniqueId);
                self.lightbox.close();
            }));
    }

});


zeit.cms.DropObjectWidget = gocept.Class.extend({

    construct: function(element, accept) {
        var self = this;
        self.element = element;
        self.input = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', null, self.element);
        self.details = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'object-reference', self.element);
        new MochiKit.DragAndDrop.Droppable(self.element, {
            accept: accept,
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                    self.handleDrop(element);
                    }});
        MochiKit.Signal.connect(
            self.element, 'onclick', self, self.handleClick);
        self.update_details();
    },

    handleDrop: function(element) {
        var self = this;
        self.input.value = element.uniqueId;
        self.changed();
        self.update_details();
    },

    remove: function() {
        var self = this;
        self.input.value = '';
        self.changed();
        self.update_details();
    },

    changed: function() {
        var self = this;
        MochiKit.Signal.signal(
            self.input, 'onchange', {target: self.input});
    },

    update_details: function() {
        var self = this;
        if (self.input.value) {
            MochiKit.DOM.addElementClass(self.element, 'busy');
            var d = zeit.cms.load_object_details(self.input.value);
            d.addCallbacks(
                function(result) {
                    self.details.innerHTML = result;
                    self.details.insertBefore(
                        A({href: '#', rel: "remove", title: "Entfernen"}),
                        self.details.firstChild);
                    return result;
                },
                function(error) {
                    self.etails.innerHTML = 'Fehler';
                    return error;
                });
            d.addBoth(function(result) {
                MochiKit.DOM.removeElementClass(self.element, 'busy');
                MochiKit.DOM.removeElementClass(self.element, 'landing-zone');
                MochiKit.DOM.removeElementClass(self.element, 'visible');
                });
        } else {
            self.details.innerHTML =
                'Ziehen Sie Inhalte hierher um sie zu verknüpfen.';
            MochiKit.DOM.addElementClass(self.element, 'landing-zone');
            MochiKit.DOM.addElementClass(self.element, 'visible');
        }
    },

    handleClick: function(event) {
        var self = this;
        var target = event.target();
        var action;
        var argument;
        if (target.nodeName == 'A' &&
            target.rel) {
            action = target.rel;
            argument = target.getAttribute('href');
        }
        if (action) {
            self[action](argument);
            event.stop();
        }
    }

});


zeit.cms._load_object_details_cache = {};

zeit.cms.load_object_details = function(uniqueId) {
    var content = zeit.cms._load_object_details_cache[uniqueId];
    var d = new MochiKit.Async.Deferred();
    if (isUndefinedOrNull(content)) {
        d = MochiKit.Async.doSimpleXMLHttpRequest(
            application_url + '/@@redirect_to', {
            unique_id: uniqueId,
            view: '@@object-details'});
        d.addCallback(function(result) {
            // Store the result for later use. This is just magnitudes
            // faster than an HTTP request.
            zeit.cms._load_object_details_cache[uniqueId] =
                result.responseText;
            return result.responseText;
        });
    } else {
        d = new MochiKit.Async.Deferred();
        d.callback(content);
    }
    return d;
};
