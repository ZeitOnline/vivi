zeit.content.cp.library = {}

MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {

    var connect_draggables = function(view, draggables) {
        var modules = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'module', view.target_id);
        forEach(modules, function(module) {
            draggables.push(
                new MochiKit.DragAndDrop.Draggable(module, {
                    zindex: null,
            }));
        });
    };

    var disconnect_draggables = function(draggables) {
        while(draggables.length) {
            draggables.pop().destroy();
        }
    };

    var create_library = function(element_id, title) {
        var url = $(element_id).getAttribute('cms:url') +
            '/@@block-factories.json';
        var library_id = 'library-' + element_id;
        var view = new zeit.cms.JSONView(url, library_id);
        tabs.add(new zeit.cms.ViewTab(library_id, title, view));
        var draggables = []

        MochiKit.Signal.connect(view, 'before-load', function() {
            disconnect_draggables(draggables);
        });
        MochiKit.Signal.connect(view, 'load', function() {
            connect_draggables(view, draggables);
        });
    }

    var tabs = new zeit.cms.Tabs('cp-library');
    create_library('cp-informatives-inner', 'Informatives');
    create_library('cp-teasermosaic', 'Mosaic');

    MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'start',
        function(draggable)  {
            if (!MochiKit.DOM.hasElementClass(draggable.element, 'module')) {
                return
            }
            var area = draggable.element.getAttribute('cms:area');
            draggable.element = draggable.element.cloneNode(true);
            MochiKit.DOM.addElementClass(
                draggable.element, 'module-drag-pane');
            draggable.offset = [-10, -10];
            $('body').appendChild(draggable.element);
    });

    MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'end',
        function(draggable) {
            if (MochiKit.DOM.hasElementClass(
                draggable.element, 'module-drag-pane')) {
                MochiKit.DOM.removeElement(draggable.element);
            }
    });

});

(function()  {
    zeit.content.cp.drop.registerHandler({ 
        accept: ['informatives-module'],
        activated_by: 'action-informatives-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type')};
        },
    });
    zeit.content.cp.drop.registerHandler({ 
        accept: ['teaser-mosaic-module'],
        activated_by: 'action-teaser-mosaic-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type')};
        },
    });
})();
