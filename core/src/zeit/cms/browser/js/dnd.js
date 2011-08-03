// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt


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
    element.is_content_object = true;
    element.drop_query_args = drop_query_args;
    return new MochiKit.DragAndDrop.Draggable(element, default_options);
};


(function() {

MochiKit.Signal.connect(
    MochiKit.DragAndDrop.Draggables, 'start', function(draggable) {
    // Generic handler for displaying the drag pane for draggables
    log("Dragging", draggable);
    if (!draggable.element.is_content_object) {
        return;
    }

    var unique_id_element = MochiKit.DOM.getFirstElementByTagAndClassName(
             'span', 'uniqueId', draggable.element);
    var uniqueId = unique_id_element.textContent;
    var dim = null;
    if (draggable.element.nodeName != 'TR') {
        dim = MochiKit.Style.getElementDimensions(draggable.element);
    }

    var div = $('drag-pane');
    if (div) {
        div.parentNode.removeChild(div);
    }
    div = DIV({'id': 'drag-pane', 'class': 'content-drag-pane'});
    div.appendChild(draggable.element.cloneNode(true));
    div.dragged_element = draggable.element;
    div.uniqueId = uniqueId;
    div.drop_query_args = draggable.element.drop_query_args || {};

    forEach(
        draggable.element.getAttribute('class').split(' '), function(class_) {
            if (class_.indexOf('type-') == 0) {
                MochiKit.DOM.addElementClass(div, class_);
            }
    });

    draggable.element = div;
    draggable.offset = [-10, -10];

    $('body').appendChild(div);
    if (!isNull(dim)) {
        MochiKit.Style.setElementDimensions(div, dim);
    }
});


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


// set up draggables for breadcrumbs
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

})();
