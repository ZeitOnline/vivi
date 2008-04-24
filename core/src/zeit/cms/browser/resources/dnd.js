// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(MochiKit.DragAndDrop.Draggables, 'start', function(draggable) {
    // Generic handler for displaying the drag pane for draggables
    log("Dragging", draggable);
    var drag_pane_url = draggable.element.drag_pane_url;
    if (drag_pane_url == undefined) {
        try {
            var base_url = getFirstElementByTagAndClassName(
             'span', 'URL', draggable.element).textContent;
            drag_pane_url  = base_url + '/@@drag-pane.html';
        } catch (e) {
        }
    }
    if (drag_pane_url == undefined) {
        return;
    }

    var div = getElement('drag-pane');
    if (div) {
        div.parentNode.removeChild(div);
    }
    div = document.createElement('div');
    div.id = 'drag-pane';
    div.dragged_element = draggable.element;
   
    var content = getElement('body');
    
    content.appendChild(div);
    draggable.element = div;
    draggable.offset = [0, 0];
   
    log("Requesting", drag_pane_url);
    var d = doSimpleXMLHttpRequest(drag_pane_url);
    d.addCallbacks(
        function(result) {
            div.innerHTML = result.responseText;
            var unique_id = getElementsByTagAndClassName(
                'div', 'UniqueId', div)[0].textContent;
            div.uniqueId = unique_id;
            return result;
        });
});


connect(MochiKit.DragAndDrop.Draggables, 'end', function(draggable) {
    // Generic handler for hiding the drag pane after dragging ended.
    var element = draggable.element;
    var dragged_element = element.dragged_element;
    if (dragged_element == undefined) return;
    draggable.element = dragged_element;
    MochiKit.Visual.switchOff(element);
});


zeit.cms.TableSorter = Class.extend({
    // Infrastructure to sort tables
    // Reorders the table on the browser.

    construct: function(class_name) {
        var othis = this;
        var table = getFirstElementByTagAndClassName('table', class_name);
        forEach(table.rows, function(row) {
            if (row.cells[0].nodeName == 'TD') {
                new Draggable(row, {
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


var ObjectReferenceWidget = Class.extend({
    // Widget for referencing one object via unique id.
    // 
    // This is also thought to be used multiple times in one formlib field,
    // e.g. for Tuple fields.

    construct: function(element, default_browsing_url, type_filter,
                        show_popup) {
        this.element = $(element);
        this.default_browsing_url = default_browsing_url;
        this.type_filter = type_filter;
        this.input = getFirstElementByTagAndClassName(
            'input', 'object-reference', this.element);
        this.input.object_reference_widget = this;
        this.changed = false;

        var othis = this;
        new Droppable(this.element, {
            hoverclass: 'drop-widget-hover',
            ondrop: function(element, last_active_element, event) {
                    othis.handleDrop(element);
            },
        });
        connect(element, 'onclick', this, 'handleClick');
        connect(this.input, 'onchange', function(event) {
            othis.changed = true;
        });

        // this saves a click and shows the object browser initially
        if (show_popup) {
            // Defer popup loading until page is completed to allow others to
            // set a unique id. 
            connect(window, 'onload', function() {
                if (!othis.input.value) 
                    othis.browseObjects();
            });
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
            var action = target.getAttribute('name');
        } else if (target.nodeName == 'A') {
            action = "handleNewUrl";
            argument = target.href;
        } else if (target.nodeName == 'TD') {
            var tr = target.parentNode;
            var url_node = getFirstElementByTagAndClassName(
                'span', 'uniqueId', tr);
            if (url_node) {
                action = 'handleObjectSelected';
                argument = url_node.textContent;
            }
        }


        if (action) {
            event.stop();
            var func = bind(action, this);
            func(argument);
        }
    },

    handleNewUrl: function(url) {
        var scroll_state = new zeit.cms.ScrollStateRestorer('popup-navtree');
        scroll_state.rememberScrollState();
        this.loadContentFromUrl(url);
    },

    handleObjectSelected: function(unique_id) {
        this.lightbox.close();
        this.selectObject(unique_id);
    },

    browseObjects: function() {
        this.lightbox = new gocept.Lightbox($('body'));
        connect(this.lightbox.content_box, 'onclick', this, 'handleClick');
        this.loadContentFromUrl(this.default_browsing_url);
    },

    showReferencedObject: function() {
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
        window.location = url;
    },

    selectObject: function(unique_id) {
        this.changed = true;
        this.input.value = unique_id;
    },

    getObject: function() {
        return this.input.value;
    },

    loadContentFromUrl: function(url) {
        var d = this.lightbox.load_url(
            url + '/@@get_object_browser',
            {type_filter: this.type_filter});
        var othis = this;
        d.addCallback(function(result) {
            var url = getFirstElementByTagAndClassName(
                'div', 'tree-view-url', othis.lightbox.content_box).innerHTML;
            var navtree = new Tree(url, 'popup-navtree');
            var scroll_state = new zeit.cms.ScrollStateRestorer('popup-navtree');
            scroll_state.restoreScrollState();
            return result;
        });
        return d;
    },
});


zeit.cms.ObjectReferenceSequenceWidget = Class.extend({

    construct: function(widget_id) {
        this.widget_id = widget_id;
        this.element = $(widget_id);
        this.form = getFirstParentByTagAndClassName(this.element, 'form');
        var othis = this;
        new Droppable(this.element, {
            hoverclass: 'drop-widget-hover',
            ondrop: function(element, last_active_element, event) {
                    othis.handleDrop(element);
            },
        });
        this.setObject();
    },

    handleDrop: function(element) {
        // On drop we create a new field
        setCookie(this.widget_id, element.uniqueId);
        var add_button = this.form[this.widget_id + '.add'];
        add_button.click();
    },

    setObject: function() {
        var unique_id =  getCookie(this.widget_id);
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
        setCookie(this.widget_id, '');
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
connect(window, 'onload', function(event) {
    var lis = $('breadcrumbs').getElementsByTagName('li');
    forEach(lis, function(li) {
        if (getFirstElementByTagAndClassName('span', 'URL', li) != undefined) {
            new Draggable(li, {
                    starteffect: null,
                    endeffect: null});
        }
    });

});
