// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt


zeit.cms.ObjectSequenceWidget = gocept.Class.extend({

    DEFAULT_HINT: 'Ziehen Sie Inhalte hierher um sie zu verknüpfen.',

    construct: function(widget_id, accept, detail_view_name, description,
                        cache_object_details) {
        var self = this;
        self.widget_id = widget_id;
        self.accept = accept;
        self.element = $(widget_id);
        self.ul_element = MochiKit.DOM.getFirstElementByTagAndClassName(
            'ul', null, self.element);
        self.url_input = $(self.widget_id + '.url');

        self.detail_view_name = detail_view_name;
        self.description = description || self.DEFAULT_HINT;
        self.cache_object_details = cache_object_details;

        self.initialize_autocomplete();
        self.initialize();
        // XXX Need to unregister those events
        MochiKit.Signal.connect(
            self.element, 'onclick', self, self.handleClick);
        if (!isNull(self.url_input)) {
            MochiKit.Signal.connect(
                self.url_input, 'onchange', self, self.handleUrlChange);
        }
        new zeit.cms.ContentDroppable(self.element, {
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
            focus: function(event, ui) {
                jQuery(self.autocomplete).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                self.add(ui.item.value);
                jQuery(self.autocomplete).val('');
                return false;
            },
            appendTo: self.element
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
        var landing_zone = MochiKit.DOM.getFirstElementByTagAndClassName(
            '*', 'landing-zone-candidate', self.element);
        if (i == 0 && isNull(self.autocomplete)) {
            self.ul_element.appendChild(LI(
                {'class': 'new'}, self.description));
            MochiKit.DOM.addElementClass(landing_zone, 'landing-zone');
            MochiKit.DOM.addElementClass(landing_zone, 'visible');
        } else {
            MochiKit.DOM.removeElementClass(landing_zone, 'landing-zone');
            MochiKit.DOM.removeElementClass(landing_zone, 'visible');
        }
    },

    renderElement: function(index, uniqueId) {
        var self = this;
        var li_id = self.widget_id + '_sort_li_' + index;
        var li = LI({
            'class': 'object-reference element busy',
            'index': index, 'id': li_id});
        var d = zeit.cms.load_object_details(
            uniqueId, self.detail_view_name, self.cache_object_details);
        d.addCallback(function(result) {
            li.innerHTML = result;
            jQuery(li).trigger_fragment_ready();
            return result;
        });
        d.addErrback(function(error) {
            zeit.cms.log_error(error);
            li.innerHTML = "Fehler beim Laden: " + uniqueId;
            return error;
        });
        d.addBoth(function(result) {
            // XXX proper i18n
            li.appendChild(A({href: index, rel: "remove",
                               title: "Entfernen", text: 'löschen'}),
                            li.firstChild);
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
        if (target.nodeName == 'A' && target.target) {
            return;
        }
        if (target.nodeName == 'A' &&
            target.rel) {
            action = target.rel;
            argument = target.getAttribute('href');
        }
        if (action) {
            self[action](argument);
            event.stop();
        }
    },

    handleUrlChange: function(event) {
        var self = this;
        var unique_id = self.url_input.value;  // XXX assumption subject to #10737
        if (unique_id) {
            self.add(unique_id);
        }
    },

    handleDrop: function(element) {
        var self = this;
        if (MochiKit.DOM.isChildNode(element, self.ul_element)) {
            return;
        }
        var unique_id = element.uniqueId;
        if (unique_id) {
            element.drag_successful = true;
            self.add(unique_id);
        }
    },

    changed: function() {
        var self = this;
        jQuery(self.getCountField()).trigger('change');
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

    configure_search: function() {
        var self = this;
        var types = MochiKit.Base.map(
            function(x) { return x.replace('type-', ''); }, self.accept);
        zeit.cms.activate_objectbrowser(types);
    }

});


zeit.cms.DropObjectWidget = gocept.Class.extend({

    construct: function(element, accept, detail_view_name, description,
                        cache_object_details) {
        var self = this;
        self.element = element;
        self.detail_view_name = detail_view_name;
        self.accept = accept;
        self.description =
            description || zeit.cms.ObjectSequenceWidget.prototype.DEFAULT_HINT;
        self.cache_object_details = cache_object_details;

        self.input = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', null, self.element);
        self.details = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'object-reference', self.element);
        self.url_input = $(self.element + '.url');

        new zeit.cms.ContentDroppable(self.element, {
            accept: self.accept,
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                    self.handleDrop(element);
                    }});
        MochiKit.Signal.connect(
            self.element, 'onclick', self, self.handleClick);
        self.update_details();
        if (!isNull(self.url_input)) {
            MochiKit.Signal.connect(
                self.url_input, 'onchange', self, self.handleUrlChange);
        }
    },

    set: function(value) {
        var self = this;
        self.input.value = value;
        self.changed();
        self.update_details();
    },

    handleUrlChange: function(event) {
        var self = this;
        var unique_id = self.url_input.value;  // XXX assumption subject to #10737
        if (unique_id) {
            self.set(unique_id);
        }
    },

    handleDrop: function(element) {
        var self = this;
        element.drag_successful = true;
        self.set(element.uniqueId);
    },

    remove: function() {
        var self = this;
        self.set('');
    },

    changed: function() {
        var self = this;
        jQuery(self.input).trigger('change');
    },

    update_details: function() {
        var self = this;
        var landing_zone = MochiKit.DOM.getFirstElementByTagAndClassName(
            '*', 'landing-zone-candidate', self.element);
        if (self.input.value) {
            MochiKit.DOM.addElementClass(self.element, 'busy');
            var d = zeit.cms.load_object_details(
                self.input.value, self.detail_view_name,
                self.cache_object_details);
            d.addCallback(function(result) {
                self.details.innerHTML = result;
                jQuery(self.details).trigger_fragment_ready();
                return result;
            });
            d.addErrback(function(error) {
                zeit.cms.log_error(error);
                MochiKit.DOM.addElementClass(self.details, 'error');
                self.details.innerHTML = (
                    'Fehler beim Laden: ' + self.input.value);
                return error;
            });
            d.addBoth(function(result) {
                self.details.appendChild(
                    A({href: '#', rel: "remove", title: "Entfernen",
                       text: 'löschen'}),
                    self.details.firstChild);
                MochiKit.DOM.removeElementClass(self.element, 'busy');
                MochiKit.DOM.removeElementClass(landing_zone, 'landing-zone');
                MochiKit.DOM.removeElementClass(landing_zone, 'visible');
                });
        } else {
            self.details.innerHTML = self.description;
            MochiKit.DOM.addElementClass(landing_zone, 'landing-zone');
            MochiKit.DOM.addElementClass(landing_zone, 'visible');
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
    },

    configure_search: function() {
        // XXX copy&paste from ObjectSequenceWidget
        var self = this;
        var types = MochiKit.Base.map(
            function(x) { return x.replace('type-', ''); }, self.accept);
        zeit.cms.activate_objectbrowser(types);
    }
});


zeit.cms._load_object_details_cache = {};

zeit.cms.load_object_details = function(uniqueId, detail_view_name, use_cache) {
    if (isUndefinedOrNull(use_cache)) {
        use_cache = true;
    }
    var cache_key = uniqueId + detail_view_name;

    var content = (
        use_cache ? zeit.cms._load_object_details_cache[cache_key] : null);
    var d = new MochiKit.Async.Deferred();
    if (isUndefinedOrNull(content)) {
        d = MochiKit.Async.doSimpleXMLHttpRequest(
            application_url + '/@@redirect_to', {
            unique_id: uniqueId,
            view: detail_view_name});
        d.addCallback(function(result) {
            if (use_cache) {
                // Store the result for later use. This is just magnitudes
                // faster than an HTTP request.
                zeit.cms._load_object_details_cache[cache_key] =
                    result.responseText;
            }
            return result.responseText;
        });
    } else {
        d = new MochiKit.Async.Deferred();
        d.callback(content);
    }
    return d;
};


(function($) {

$(document).bind('fragment-ready', function(event) {
    $('.content-icon', event.__target).each(function(i, element) {
       zeit.cms.createDraggableContentObject(element);
    });
});

}(jQuery));
