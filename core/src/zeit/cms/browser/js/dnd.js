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
    element.drop_query_args = drop_query_args;
    // mark so draggable event handlers (below) can recognize it
    element.is_content_object = true;
    return new MochiKit.DragAndDrop.Draggable(element, default_options);
};


(function() {

/**
 Draggables move their .element around, but here we want to leave the original
 element (the "source element") in its place and drag a copy around. So we
 replace the draggable.element with a custom-created div.drag-pane, and clone
 the original draggable.element into it.
 */
MochiKit.Signal.connect(
    MochiKit.DragAndDrop.Draggables, 'start', function(draggable) {
    log("Dragging", draggable);
    if (!draggable.element.is_content_object) {
        return;
    }

    var div = $('drag-pane');
    if (div) {
        div.parentNode.removeChild(div);
    }
    div = DIV({'id': 'drag-pane', 'class': 'content-drag-pane'});

    var source_element = draggable.element;
    div.source_element = source_element;
    div.appendChild(source_element.cloneNode(true));

    // copy over information onto the drag-pane so it's easily accessible for
    // drop handlers
    var uniqueId = MochiKit.DOM.getFirstElementByTagAndClassName(
             'span', 'uniqueId', source_element).textContent;
    div.uniqueId = uniqueId;
    div.drop_query_args = source_element.drop_query_args || {};

    // the type-* class is used as an accept filter by ObjectSequenceWidget and
    // DropObjectWidget, so the drag-pane needs to have those too to be
    // droppable there
    forEach(
        source_element.getAttribute('class').split(' '), function(class_) {
            if (class_.indexOf('type-') == 0) {
                MochiKit.DOM.addElementClass(div, class_);
            }
    });

    draggable.element = div;
    draggable.offset = [-10, -10];
    $('body').appendChild(div);

    var dim = null;
    if (source_element.nodeName != 'TR') {
        dim = MochiKit.Style.getElementDimensions(source_element);
    }
    if (!isNull(dim)) {
        MochiKit.Style.setElementDimensions(div, dim);
    }
});


// remove drag-pane and restore draggable.element
MochiKit.Signal.connect(
    MochiKit.DragAndDrop.Draggables, 'end', function(draggable) {
    var drag_pane = draggable.element;
    if (isUndefinedOrNull(drag_pane.source_element)) {
        return;
    }
    draggable.element = drag_pane.source_element;
    MochiKit.Visual.fade(drag_pane);
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
