// Copyright (c) 2007 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(MochiKit.DragAndDrop.Draggables, 'start', function(draggable) {
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


//Defines the top level Class
function Class() { }
Class.prototype.construct = function() {};
Class.extend = function(def) {
  var classDef = function() {
      if (arguments[0] !== Class) { this.construct.apply(this, arguments); }
  };

  var proto = new this(Class);
  var superClass = this.prototype;

  for (var n in def) {
      var item = def[n];                      
      if (item instanceof Function) item.$ = superClass;
      proto[n] = item;
  }

  classDef.prototype = proto;

  //Give this new class the same static extend method    
  classDef.extend = this.extend;      
  return classDef;
};


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
                LI({'class': 'element', 'index': i},
                   title,
                   IMG({
                       'action': 'delete',
                       'index': i,
                       'src': '/@@/zeit.cms/icons/delete.png'})));
        });
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
        this.decreaseCount()
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
