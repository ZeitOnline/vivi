// Copyright (c) 2007-2010 gocept gmbh & co. kg
// See also LICENSE.txt

MochiKit.Signal.connect(
    MochiKit.DragAndDrop.Draggables, 'start', function(draggable) {
    // Generic handler for displaying the drag pane for draggables
    log("Dragging", draggable);
    if (!draggable.element.is_content_object) {
        return;
    }
    var pane_clone_from = draggable.element.pane_element;
    var uniqueId = draggable.element.textContent;
    var dim = null;
    if (pane_clone_from.nodeName != 'TR') {
        dim = MochiKit.Style.getElementDimensions(pane_clone_from); 
    }

    var div = $('drag-pane');
    if (div) {
        div.parentNode.removeChild(div);
    }
    div = DIV({'id': 'drag-pane', 'class': 'content-drag-pane'});
    div.appendChild(pane_clone_from.cloneNode(true));
    div.dragged_element = draggable.element;
    div.uniqueId = uniqueId;
    div.drop_query_args = draggable.element.drop_query_args || {};
    
    draggable.element = div;
    draggable.offset = [-10, -10];

    $('body').appendChild(div);
    if (!isNull(dim)) {
        MochiKit.Style.setElementDimensions(div, dim);
    }
});


(function() {

    MochiKit.Signal.connect(
        MochiKit.DragAndDrop.Draggables, 'end', function(draggable) {
        // Generic handler for hiding the drag pane after dragging ended.
        var element = draggable.element;
        var dragged_element = element.dragged_element;
        if (isUndefinedOrNull(dragged_element)) {
            return;
        }
        draggable.element = dragged_element;
        MochiKit.Visual.fade(element);
    });
})();


zeit.cms.createDraggableContentObject = function(element, options) {
    element = $(element);
    var default_options = {
        drop_query_args: {},
        endeffect: null,
        handle: element,
        starteffect: null,
        zindex: null
    };
    MochiKit.Base.update(default_options, options);
    var drop_query_args = default_options['drop_query_args'];
    delete default_options['drop_query_args'];
    var unique_id_element = MochiKit.DOM.getFirstElementByTagAndClassName(
             'span', 'uniqueId', element);
    unique_id_element.pane_element = element;
    unique_id_element.is_content_object = true;
    unique_id_element.drop_query_args = drop_query_args;
    //element.uniqueId = unique_id_element.textContent;
    return new MochiKit.DragAndDrop.Draggable(
        unique_id_element, default_options);
};


zeit.cms.TableSorter = gocept.Class.extend({
    // Infrastructure to sort tables
    // Reorders the table on the browser.

    construct: function(class_name) {
        var othis = this;
        var table = MochiKit.DOM.getFirstElementByTagAndClassName(
            'table', class_name);
        forEach(table.rows, function(row) {
            if (row.cells[0].nodeName == 'TD') {
                new MochiKit.DragAndDrop.Draggable(row, {
                    ghosting: true
                });
            }
            
            new Droppable(row, {
                ondrop: function (element) {
                    var tbody = element.parentNode;
                    if (tbody.nodeName != 'TBODY') {
                        // TODO: i18n
                        alert('The table can only be sorted. ' +
                              'Adding is not possible.');
                        return;
                    }
                    var before = null;
                    if (row.cells[0].nodeName == 'TH') {
                        before = tbody.firstChild;
                    } else {
                        before = row.nextSibling;
                    }
                    if (before) {
                        tbody.insertBefore(element, before);
                    } else {
                        tbody.appendChild(element);
                    }
                    othis.dropped(element);
                },
                hoverclass: 'tablesort-hover'
            });
        });
    
    },

    dropped: function(element) {
        // pass
    }

});


zeit.cms.ObjectAddForm = zeit.cms.LightboxForm.extend({
    process_post_result: function(result) {
        var self = this;

        if (self.has_errors()) {
            return result;
        }

        // enable the visual effect to work
        MochiKit.DOM.removeElementClass(self.container, 'busy');

        var node = getFirstElementByTagAndClassName(
            'span', 'result', self.container);
        var unique_id = node.textContent;
        MochiKit.Signal.signal(
            self, 'zeit.cms.ObjectReferenceWidget.selected',
            unique_id, node);
        return null;
    }

});


var ObjectReferenceWidget = gocept.Class.extend({
    // Widget for referencing one object via unique id.
    // 
    // This is also thought to be used multiple times in one formlib field,
    // e.g. for Tuple fields.

    construct: function(element, default_browsing_url, type_filter,
                        add_view, show_popup, parent_component) {
        var self = this;
        self.events = [];

        self.element = $(element);
        self.default_browsing_url = default_browsing_url;
        self.type_filter = type_filter;
        self.add_view = add_view;
        self.input = getFirstElementByTagAndClassName(
            'input', 'object-reference', self.element);
        self.input.object_reference_widget = self;
        self.changed = false;
        self.parent_component = parent_component;

        self.droppable = new MochiKit.DragAndDrop.Droppable(self.element, {
            accept: ['content-drag-pane', 'uniqueId'],
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                    self.handleDrop(element);
            }
        });

        self.events.push(
            MochiKit.Signal.connect(
                element, 'onclick', self, self.handleClick));
        self.events.push(
            MochiKit.Signal.connect(self.input, 'onchange', function(event) {
                self.changed = true;
        }));

        self.tooltip = new zeit.cms.ToolTip(element, function() {
            return self.getToolTipURL();
        });

        var addbutton = getFirstElementByTagAndClassName(
            'input', 'add-object', self.element);
        if (isUndefinedOrNull(self.add_view)) {
            MochiKit.DOM.hideElement(addbutton);
        } else {
            MochiKit.DOM.addElementClass(self.element, 'add-button');
        }

        // self saves a click and shows the object browser initially
        if (show_popup && isUndefinedOrNull(parent_component)) {
            // Defer popup loading until page is completed to allow others to
            // set a unique id. 
            self.events.push(MochiKit.Signal.connect(
                window, 'onload', function() {
                    if (!self.input.value) 
                        self.browseObjects();
            }));
        }

        if (!isUndefinedOrNull(parent_component)) {
            self.events.push(MochiKit.Signal.connect(
                parent_component, 'close', self, self.destruct));
        }
    },

    destruct: function() {
        var self = this;
        self.tooltip.destruct();
        self.droppable.destroy();
        while (self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        }
    },

    handleDrop: function(element) {
        this.selectObject(element.uniqueId);
    },

    handleClick: function(event) {
        var target = event.target();
        var action = null;
        var argument;
        if (target.nodeName == 'INPUT' && target.type == 'button') {
            event.stop();
            action = target.getAttribute('name');
            var func = bind(action, this);
            func(event);
        }
    },

    handleObjectSelected: function(unique_id, element) {
        var self = this;
        if (isUndefinedOrNull(element)) {
            self.lightbox.close();
            self.lightbox = null;
            self.selectObject(unique_id);
        } else { 
            MochiKit.Style.makePositioned(element);
            var pos = MochiKit.Style.getElementPosition(element);
            var cloned_element = element.cloneNode(true);
            $('body').appendChild(cloned_element);
            MochiKit.Style.setcloned_elementPosition(cloned_element, pos);
            MochiKit.Style.makeClipping(cloned_element);
            self.lightbox.close();
            self.lightbox = null;
            // Visual candy
            pos = MochiKit.Style.getcloned_elementPosition(self.input);
            var move = new MochiKit.Visual.Move(cloned_element, {
                mode: 'absolute',
                sync: true,
                x: pos.x,
                y: pos.y
            });
            var shrink = MochiKit.Visual.Scale(cloned_element, 0, {
                sync: true
            });
            new MochiKit.Visual.Parallel([move, shrink], {
                afterFinish: function() {
                    self.selectObject(unique_id);
                    cloned_element.parentNode.removeChild(cloned_element);
                }
            });
        }
    },

    browseObjects: function(event) {
        var self = this;
        if (zeit.cms.activate_objectbrowser()) {
            return;
        }
        var url = self.default_browsing_url;
        if (url.indexOf('@@') == -1) {
            url += '/@@get_object_browser';
        }
        url += '?' + MochiKit.Base.queryString(
            {type_filter: this.type_filter});
        self.lightbox = new zeit.cms.LightboxForm(url, $('body'));
        self.lightbox.events.push(MochiKit.Signal.connect(
            self.lightbox, 'zeit.cms.ObjectReferenceWidget.selected',
            self, self.handleObjectSelected));

    },

    addObject: function(event) {
        var self = this;
        var url = self.default_browsing_url + '/@@' + self.add_view;
        self.lightbox = new zeit.cms.ObjectAddForm(url, $('body'));
        self.lightbox.events.push(MochiKit.Signal.connect(
            self.lightbox, 'zeit.cms.ObjectReferenceWidget.selected',
            self, self.handleObjectSelected));
    },

    showReferencedObject: function(event) {
        var new_window = event.modifier().any;
        var unique_id = this.getObject();
        if (!unique_id) {
            return;
        }
        // XXX i18n
        var msg = 'Your changes have not been saved, yet. Continue?';
        if (this.changed && !confirm(msg)) {
            return;
        }
        var qs = MochiKit.Base.queryString({
            'unique_id': unique_id});
        var url = application_url + '/redirect_to?' + qs;
        if (new_window) {
            window.open(url);
        } else {
            window.location = url;
        }
    },

    selectObject: function(unique_id) {
        var self = this;
        self.changed = true;
        self.input.value = unique_id;
        self.input.focus();
        MochiKit.Signal.signal(self.input, 'onchange', {target: self.input});
    },

    getObject: function() {
        return this.input.value;
    },

    getToolTipURL: function() {
        var othis = this;
        var unique_id = othis.getObject();
        if (!unique_id) {
            return null;
        }
        var qs = MochiKit.Base.queryString({
            'unique_id': unique_id,
            'view': '@@drag-pane.html'});
        var url = application_url + '/redirect_to?' + qs;
        return url;
    }
});


zeit.cms.ObjectReferenceSequenceWidget = gocept.Class.extend({

    construct: function(widget_id, parent_component) {
        var self = this;
        self.widget_id = widget_id;
        self.element = $(widget_id);
        self.parent_component = parent_component;
        self.form = MochiKit.DOM.getFirstParentByTagAndClassName(
            self.element, 'form');
        var droppable_element = MochiKit.Selector.findChildElements(
            self.element,
            ['> table.sequencewidget > tbody > tr:last-child'])[0];
        self.droppable = new MochiKit.DragAndDrop.Droppable(droppable_element, {
            accept: ['content-drag-pane', 'uniqueId'],
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                    self.handleDrop(element);
            }
        });
        self.setObject();
        if (!isUndefinedOrNull(parent_component)) {
            self.events.push(MochiKit.Signal.connect(
                parent_component, 'close', self, self.destruct));
        }
    },

    destruct: function() {
        self.droppable.destroy();
    },

    handleDrop: function(element) {
        // On drop we create a new field
        zeit.cms.setCookie(this.widget_id, element.uniqueId);
        var add_button = this.form[this.widget_id + '.add'];
        add_button.click();
    },

    setObject: function() {
        var unique_id =  zeit.cms.getCookie(this.widget_id);
        if (!unique_id) {
            return;
        }
        var count = new Number(this.form[this.widget_id + '.count'].value);
        if (count <= 0) {
            return;
        }
        var field_nr = count - 1;

        var input = this.form[this.widget_id + '.' + field_nr + '.'];
        var widget = input.object_reference_widget;
        if (widget.getObject()) {
            return;
        }
        widget.selectObject(unique_id);
        zeit.cms.setCookie(this.widget_id, '');
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
            view: '@@zeit.cms.browser.object-widget-details'});
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


zeit.cms.ObjectSequenceWidget = gocept.Class.extend({

    construct: function(widget_id) {
        var self = this;
        this.widget_id = widget_id;
        this.element = $(widget_id);
        this.ul_element = getFirstElementByTagAndClassName(
            'ul', null, this.element);
        this.initialize();
        // XXX Need to unregister those events
        MochiKit.Signal.connect(this.element, 'onclick', this, 'handleClick');
        new MochiKit.DragAndDrop.Droppable(self.element, {
            accept: ['uniqueId', 'content-drag-pane'],
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                self.handleDrop(element);
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
                appendChildNodes(
                    self.ul_element,
                    self.renderElement(i, input.value));
                i += 1;
        });
        MochiKit.Sortable.create(
            self.ul_element, {
            onUpdate: function() { self.update_order_from_ul(); }
            });
        if (i == 0) {
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
        return getElement(this.widget_id + '.count');
    },

    getValueField: function(index) {
        return getElement(this.getValueFieldName(index));
    },

    getValueFieldName: function(index) {
        return this.widget_id + '.' + index;
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

        removeElement(self.getValueField(index));

        var new_index = 0;
        self.iterFields(function(value_field) {
            value_field_name = self.getValueFieldName(new_index);
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
        var amount = new Number(count_field.value);
        forEach(range(amount), function(iteration_index) {
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
        if (target.nodeName == 'A' &&
            target.rel) {
            var action = target.rel;
            var argument = target.getAttribute('href');
        }
        if (action && argument) {
            self[action](argument);
            event.stop();
        }
    },

    handleDrop: function(dragged_element) {
        var self = this;
        if (MochiKit.DOM.isChildNode(dragged_element, self.ul_element)) {
            return;
        }
        var unique_id = dragged_element.uniqueId;
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
        for (var i=0; i<ordered_ids.length; i++) {
            self.getValueField(i).value = ordered_ids[i];
        }
        self.changed();
    }

});


// Connect breadcrumbs
MochiKit.Signal.connect(window, 'onload', function(event) {
    var breadcrumbs = $('breadcrumbs');
    if (breadcrumbs === null) {
        return;
    }
    var lis = breadcrumbs.getElementsByTagName('li');
    forEach(lis, function(li) {
        if (!isUndefinedOrNull(MochiKit.DOM.getFirstElementByTagAndClassName(
            'span', 'uniqueId', li))) {
            zeit.cms.createDraggableContentObject(li);
        }
    });

});


zeit.cms.DropObjectWidget = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        self.element = element;
        self.input = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', null, self.element);
        self.details = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'object-reference', self.element);
        new MochiKit.DragAndDrop.Droppable(self.element, {
            accept: ['uniqueId', 'content-drag-pane'],
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
        self = this;
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
        if (target.nodeName == 'A' &&
            target.rel) {
            var action = target.rel;
            var argument = target.getAttribute('href');
        }
        if (action) {
            self[action](argument);
            event.stop();
        }
    }

});
