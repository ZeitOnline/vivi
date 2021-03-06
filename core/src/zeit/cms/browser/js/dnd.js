// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt

(function() {

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
    MochiKit.DOM.addElementClass(element, 'represents-content-object');
    return new MochiKit.DragAndDrop.Draggable(element, default_options);
};


zeit.cms.ContentDroppable = function(element, options) {
    // XXX Code copied from MochiKit.DragAndDrop.
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

zeit.cms.ContentDroppable.prototype = {};
MochiKit.Base.update(zeit.cms.ContentDroppable.prototype,
                     MochiKit.DragAndDrop.Droppable.prototype);
MochiKit.Base.update(zeit.cms.ContentDroppable.prototype, {
    isAccepted: function(element) {
        element = jQuery(element);
        if (!(element.hasClass('represents-content-object') ||
              element.hasClass('content-drag-pane'))) {
            return false;
        }
        if (!this.options.accept) {
            return true;
        }
        for (var i = 0; i < this.options.accept.length; i++) {
            var cls = this.options.accept[i];
            if (element.hasClass(cls)) {
                return true;
            }
        }
        return false;
    }
});


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

    MochiKit.Signal.signal(window, 'before-content-drag', draggable);
    var pos = MochiKit.Style.getElementPosition(
        draggable.element);
    draggable.delta = [pos.x, pos.y];

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
    var class_ = source_element.getAttribute('class') || '';
    forEach(
        class_.split(' '), function(class_) {
            if (class_.indexOf('type-') == 0) {
                MochiKit.DOM.addElementClass(div, class_);
            }
    });

    draggable.element = div;
    draggable.offset = [-10, -10];
    jQuery('body').append(div);

    var dim = null;
    if (source_element.nodeName != 'TR') {
        dim = MochiKit.Style.getElementDimensions(source_element);
    }
    if (!isNull(dim)) {
        MochiKit.Style.setElementDimensions(div, dim);
    }

    // XXX klugdy: prepare() (which sets the activeclass on the applicable
    // droppables) comes *before* the 'start' event (of which we are a handler).
    // But since we swap the dragged element (and change CSS classes etc.),
    // prepare() has no chance of activating droppables that match the
    // newly swapped-in element. Thus, we call it a second time and hope
    // that's not too much overhead.
    MochiKit.DragAndDrop.Droppables.prepare(div);
});


// remove drag-pane and restore draggable.element
MochiKit.Signal.connect(
    MochiKit.DragAndDrop.Draggables, 'end', function(draggable) {
        var drag_pane = draggable.element;
        if (isUndefinedOrNull(drag_pane.source_element)) {
            return;
        }

        MochiKit.DOM.addElementClass(drag_pane, 'finished');

        // Since MochiKit does not differentiate whether we successfullly
        // landed on a Droppable or not, we need to make that distinction
        // ourselves -- all Droppables need to set ``drag_successful``.
        if (drag_pane.drag_successful) {
            MochiKit.Visual.fade(drag_pane, {
                'afterFinish': function() {
                    MochiKit.DOM.removeElement(drag_pane); }});
        } else {
            // XXX copy&paste of firing reverteffect
            var d = draggable.currentDelta();
            var top_offset = d[1] - draggable.delta[1];
            var left_offset = d[0] - draggable.delta[0];
            // XXX copy&paste of default reverteffect to reuse it.
            var dur = Math.sqrt(Math.abs(top_offset^2) +
                                Math.abs(left_offset^2))*0.02;
            new MochiKit.Visual.Move(drag_pane, {
                x: -left_offset, y: -top_offset, duration: dur,
                'afterFinish': function() {
                    MochiKit.DOM.removeElement(drag_pane);
            }});
        }

        draggable.element = drag_pane.source_element;
    }
);


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

}());
