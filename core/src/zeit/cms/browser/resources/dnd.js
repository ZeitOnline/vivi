// Copyright (c) 2007 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(MochiKit.DragAndDrop.Draggables, 'start', function(draggable) {
    log("Dragging", draggable);
    var drag_pane_url = draggable.element.drag_pane_url;
    if (drag_pane_url == undefined) {
        try {
             drag_pane_url = getElementsByTagAndClassName(
                'span', 'DragPaneURL', draggable.element)[0].textContent;
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
    var element = draggable.element;
    var dragged_element = element.dragged_element;
    if (dragged_element == undefined) return;
    draggable.element = dragged_element;
    MochiKit.Visual.switchOff(element);
});


function DropWidget(element) {
    var othis = this;
    this.drop_target = getElement(element);
    new Droppable(this.drop_target, {
        hoverclass: 'drop-widget-hover',
        ondrop: function(element, last_active_element, event) {
                othis.handleDrop(element);
        },
    });
}

DropWidget.prototype = {

    handleDrop: function(element) {
        var input = getFirstElementByTagAndClassName(
            'input', 'object-reference', this.drop_target);
        input.value = element.uniqueId;
        var span = getFirstElementByTagAndClassName(
            'span', 'object-reference', this.drop_target);
        span.innerHTML = element.uniqueId;
    },
}


function ObjectSequenceWidget(widget_id) {
    var othis = this;
    this.widget_id = widget_id;
    this.element = getElement(widget_id);
    this.initialize();
    connect(this.element, 'onclick', this, 'handleClick');
    new Droppable(this.element, {
        hoverclass: 'drop-widget-hover',
        ondrop: function(element, last_active_element, event) {
            othis.handleDrop(element);
        },
    });
}


ObjectSequenceWidget.prototype = {

    initialize: function() {
        var othis = this;
        var ul = getFirstElementByTagAndClassName('ul', null, this.element)
        while (ul.firstChild != null) {
            removeElement(ul.firstChild);
        }
        var amount = Number(this.getCountField().value);
        forEach(range(amount), function(i) {
            //var value_name = this.widget_id + '.' + i;
            var title = othis.getTitleField(i).value;
            appendChildNodes(
                ul,
                LI({'class': 'element', 'index': i},
                   title,
                   IMG({
                       'action': 'delete',
                       'index': i,
                       'src': '/@@/zeit.cms/icons/delete.png'})));
        });

        var new_li = LI({'class': 'new'},
                        'Weitere Einträge durch Drag and Drop hinzufügen…');
        appendChildNodes(ul, new_li);
        othis.drop_target = new_li;
    },

    getCountField: function() {
        var othis = this;
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

    delete: function(index) {
        var othis = this;

        removeElement(this.getValueField(index));
        removeElement(this.getTitleField(index));

        var count_field = this.getCountField();
        var amount = Number(count_field.value)
        var new_index = 0;
        forEach(range(amount), function(iteration_index) {
            var value_field = othis.getValueField(iteration_index)
            var title_field = othis.getTitleField(iteration_index)
            if (value_field == null) {
                return;
            }
           
            value_field_name = othis.getValueFieldName(new_index);
            value_field.setAttribute('name', value_field_name);
            value_field.setAttribute('id', value_field_name);
            
            title_field_name = othis.getTitleFieldName(new_index);
            title_field.setAttribute('name', title_field_name);
            title_field.setAttribute('id', title_field_name);

            new_index += 1;
        });
        count_field.value = amount - 1;
        this.initialize();
    },

    handleDrop: function(dragged_element) {
        var unique_id = dragged_element.uniqueId;
        var count_field = this.getCountField()
        var count = Number(count_field.value);
        count_field.value = count + 1;

        var title_element = getFirstElementByTagAndClassName(
            null, 'Text', dragged_element);
        var title;
        if (title_element == undefined) {
            title = unique_id;
        } else {
            title = scrapeText(title_element)
        }
      
        var id_field_name = this.getValueFieldName(count);
        var title_field_name = this.getTitleFieldName(count);

        appendChildNodes(
            this.element,
            INPUT({'type': 'hidden',
                   'name': id_field_name,
                   'id': id_field_name,
                   'value': unique_id}),
            INPUT({'type': 'hidden',
                   'name': title_field_name,
                   'id': title_field_name,
                   'value': title}));
        this.initialize();        
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
}
