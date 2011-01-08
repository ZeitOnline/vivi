// Copyright (c) 2007-2011 gocept gmbh & co. kg
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
    if (pane_clone_from.nodeName == 'TR') {
        var dim = null;
    } else {
        var dim = MochiKit.Style.getElementDimensions(pane_clone_from); 
    }

    var div = $('drag-pane');
    if (div) {
        div.parentNode.removeChild(div);
    }
    div = DIV({id: 'drag-pane', class: 'content-drag-pane'});
    div.appendChild(pane_clone_from.cloneNode(true));
    div.dragged_element = draggable.element;
    div.uniqueId = uniqueId;
    div.drop_query_args = draggable.element.drop_query_args || {}
    
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
            return
        }
        draggable.element = dragged_element;
        MochiKit.Visual.fade(element);
    });
})();


zeit.cms.createDraggableContentObject = function(element, options) {
    var default_options = {
        drop_query_args: {},
        endeffect: null,
        handle: element,
        starteffect: null,
        zindex: null,
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
}


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
                              'Adding is not possible.')
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
                hoverclass: 'tablesort-hover',
            });
        });
    
    },

    dropped: function(element) {
        // pass
    },
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
    },
});


var ObjectReferenceWidget = Class.extend({
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
            },
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
            MochiKit.DOM.addElementClass(self.element, 'add-button')
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
        var action;
        var argument;
        if (target.nodeName == 'INPUT' && target.type == 'button') {
            event.stop();
            var action = target.getAttribute('name');
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
            var element = element.cloneNode(true);
            $('body').appendChild(element);
            MochiKit.Style.setElementPosition(element, pos);
            MochiKit.Style.makeClipping(element);
            self.lightbox.close();
            self.lightbox = null;
            // Visual candy
            var pos = MochiKit.Style.getElementPosition(self.input);
            var move = new MochiKit.Visual.Move(element, {
                mode: 'absolute',
                sync: true,
                x: pos.x,
                y: pos.y,
            });
            var shrink = MochiKit.Visual.Scale(element, 0, {
                sync: true
            });
            new MochiKit.Visual.Parallel([move, shrink], {
                afterFinish: function() {
                    self.selectObject(unique_id);
                    element.parentNode.removeChild(element);
                },
            })
        }
    },

    browseObjects: function(event) {
        var self = this;
        if (zeit.cms.activate_objectbrowser()) {
            return
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
            return
        }
        // XXX i18n
        var msg = 'Your changes have not been saved, yet. Continue?';
        if (this.changed && !confirm(msg)) {
            return
        }
        var qs = MochiKit.Base.queryString({
            'unique_id': unique_id});
        var url = application_url + '/redirect_to?' + qs
        if (new_window) {
            window.open(url);
        } else {
            window.location = url;
        }
    },

    selectObject: function(unique_id) {
        this.changed = true;
        this.input.value = unique_id;
        MochiKit.Signal.signal(this.input, 'onchange');
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
        var url = application_url + '/redirect_to?' + qs
        return url;
    },
});


zeit.cms.ObjectReferenceSequenceWidget = Class.extend({

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
            },
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
            return
        }
        var count = new Number(this.form[this.widget_id + '.count'].value);
        if (count <= 0) {
            return
        }
        var field_nr = count - 1;

        var input = this.form[this.widget_id + '.' + field_nr + '.'];
        var widget = input.object_reference_widget;
        if (widget.getObject()) {
            return
        }
        widget.selectObject(unique_id);
        zeit.cms.setCookie(this.widget_id, '');
    },

});



var ObjectSequenceWidgetBase = Class.extend({

    construct: function(widget_id) {
        var othis = this;
        this.widget_id = widget_id;
        this.element = getElement(widget_id);
        this.ul_element = getFirstElementByTagAndClassName(
            'ul', null, this.element)
        this.initialize();
        connect(this.element, 'onclick', this, 'handleClick');
    },

    initialize: function() {
        var othis = this;
        while (this.ul_element.firstChild != null) {
            removeElement(this.ul_element.firstChild);
        }
        var amount = Number(this.getCountField().value);
        forEach(range(amount), function(i) {
            //var value_name = this.widget_id + '.' + i;
            var title = othis.getTitleField(i).value;
            appendChildNodes(
                othis.ul_element,
                othis.renderElement(i, title));
        });
    },

    renderElement: function(index, title) {
        return LI({'class': 'element', 'index': index},
                  title, 
                  IMG({'action': 'delete',
                       'index': index,
                       'src': '/@@/zeit.cms/icons/delete.png'}));
    },

    increaseCount: function() {
        var count_field = this.getCountField()
        var count = Number(count_field.value);
        count_field.value = count + 1;
        return count_field.value;
    },
    
    decreaseCount: function() {
        var count_field = this.getCountField()
        var count = Number(count_field.value);
        count_field.value = count - 1;
        return count_field.value;
    },

    getCountField: function() {
        return getElement(this.widget_id + '.count')
    },

    getValueField: function(index) {
        return getElement(this.getValueFieldName(index));
    },

    getValueFieldName: function(index) {
        return this.widget_id + '.' + index;
    },

    getTitleField: function(index) {
        return getElement(this.getTitleFieldName(index));
    },

    getTitleFieldName: function(index) {
        return this.widget_id + '.title.' + index;
    },

    add: function(value, title) {
        var next_id = this.increaseCount() - 1;
      
        var id_field_name = this.getValueFieldName(next_id);
        var title_field_name = this.getTitleFieldName(next_id);

        appendChildNodes(
            this.element,
            INPUT({'type': 'hidden',
                   'name': id_field_name,
                   'id': id_field_name,
                   'value': value}),
            INPUT({'type': 'hidden',
                   'name': title_field_name,
                   'id': title_field_name,
                   'value': title}));
        this.initialize();        
    },

    delete: function(index) {
        var othis = this;

        removeElement(this.getValueField(index));
        removeElement(this.getTitleField(index));

        var new_index = 0;
        this.iterFields(function(value_field, title_field) {
            value_field_name = othis.getValueFieldName(new_index);
            value_field.setAttribute('name', value_field_name);
            value_field.setAttribute('id', value_field_name);
            
            title_field_name = othis.getTitleFieldName(new_index);
            title_field.setAttribute('name', title_field_name);
            title_field.setAttribute('id', title_field_name);

            new_index += 1;
        });
        this.decreaseCount()
        this.initialize();
    },

    iterFields: function(callable) {
        var othis = this;
        var count_field = this.getCountField();
        var amount = Number(count_field.value)
        forEach(range(amount), function(iteration_index) {
            var value_field = othis.getValueField(iteration_index);
            var title_field = othis.getTitleField(iteration_index);
            if (value_field === null) {
                return;
            }
            callable(value_field, title_field);
        });
    },

    handleClick: function(event) {
        var target = event.target();
        var action = target.getAttribute('action');
        var index = target.getAttribute('index');
        if (action && index) {
            var func = bind(action, this);
            func(index);
        }
    },


});


var ObjectSequenceWidget = ObjectSequenceWidgetBase.extend({

    construct: function(widget_id) {
        arguments.callee.$.construct.call(this, widget_id)
        var othis = this;
        new Droppable(this.element, {
            hoverclass: 'drop-widget-hover',
            ondrop: function(element, last_active_element, event) {
                othis.handleDrop(element);
            },
        });
    },

    initialize: function() {
        arguments.callee.$.initialize.call(this);
        var new_li = LI({'class': 'new'},
                        'Weitere Einträge durch Drag and Drop hinzufügen…');
        appendChildNodes(this.ul_element, new_li);
        this.drop_target = new_li;
    },

    handleDrop: function(dragged_element) {
        var unique_id = dragged_element.uniqueId;
        var title_element = getFirstElementByTagAndClassName(
            null, 'Text', dragged_element);
        var title;
        if (title_element == undefined) {
            title = unique_id;
        } else {
            title = scrapeText(title_element)
        }
        arguments.callee.$.add.call(this, unique_id, title);
    },

});


// Connect breadcrumbs
MochiKit.Signal.connect(window, 'onload', function(event) {
    var breadcrumbs = $('breadcrumbs')
    if (breadcrumbs == null) {
        return
    }
    var lis = breadcrumbs.getElementsByTagName('li');
    forEach(lis, function(li) {
        if (!isUndefinedOrNull(MochiKit.DOM.getFirstElementByTagAndClassName(
            'span', 'uniqueId', li))) {
            zeit.cms.createDraggableContentObject(li);
        }
    });

});
