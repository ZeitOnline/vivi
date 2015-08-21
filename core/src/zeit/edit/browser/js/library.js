(function() {

zeit.cms.declare_namespace('zeit.edit.library');

// Internal functions

var connect_draggables = function(view, draggables) {
    var modules = MochiKit.DOM.getElementsByTagAndClassName(
        'div', 'module', view.target_id);
    forEach(modules, function(module) {
        draggables.push(
            new MochiKit.DragAndDrop.Draggable(module, {
                zindex: null
        }));
    });
};

var disconnect_draggables = function(draggables) {
    while(draggables.length) {
        draggables.pop().destroy();
    }
};

// public API
zeit.edit.library.create_for_element = function(element_id, title) {
    var url = $(element_id).getAttribute('cms:url');
    var library_id = 'library-' + element_id;
    zeit.edit.library.create(library_id, url, title);
};

zeit.edit.library.create = function(library_id, url, title, view_name) {
    if (!view_name) {
        view_name = '@@block-factories.json';
    }
    url = url + '/' + view_name;
    var view = new zeit.cms.JSONView(url, library_id);
    zeit.edit.library.tabs.add(new zeit.cms.ViewTab(library_id, title, view, {
        render_on_activate: true}));
    var draggables = [];

    MochiKit.Signal.connect(view, 'before-load', function() {
        disconnect_draggables(draggables);
    });
    MochiKit.Signal.connect(view, 'load', function() {
        connect_draggables(view, draggables);
    });
};


// Internal functions

MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    zeit.edit.library.tabs = new zeit.cms.Tabs('cp-library');
});

MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'start',
    function(draggable)  {
        if (!MochiKit.DOM.hasElementClass(draggable.element, 'module')) {
            return;
        }

        // XXX It's unclear which semantics we want here: A generic before-drag
        // event, or specific before-content-drag, before-module-drag etc.?
        // Since there is only one subscriber at the moment, we leave it as is.
        MochiKit.Signal.signal(window, 'before-content-drag', draggable);

        // XXX This copies most of the mechanics of zeit.cms:dnd.js,
        // but now we benefit from its drag-end handler that distinguishes
        // between success/failure.
        var source_element = draggable.element;
        var pos = MochiKit.Style.getElementPosition(
            source_element);
        draggable.delta = [pos.x, pos.y];
        draggable.element = source_element.cloneNode(true);
        draggable.element.source_element = source_element;
        draggable.offset = [-10, -10];
        jQuery('body').append(draggable.element);
});

}());
