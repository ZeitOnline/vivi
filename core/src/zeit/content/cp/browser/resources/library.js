(function() {

MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (! zeit.cms.in_cp_editor()) {
        return;
    }

    zeit.edit.library.create('all', context_url, 'Alle');
    zeit.edit.library.create('area', context_url, 'Flächen', '@@area-factories.json');
});


MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    if (! zeit.cms.in_cp_editor()) {
        return;
    }

    zeit.edit.drop.registerHandler({
        accept: ['cp-module'],
        activated_by: 'action-cp-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type')};
        }
    });

    zeit.edit.drop.registerHandler({
        accept: ['region-module'],
        activated_by: 'action-cp-region-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type'),
                    'block_params': draggable.getAttribute('cms:block_params')};
        }
    });

});

}());
