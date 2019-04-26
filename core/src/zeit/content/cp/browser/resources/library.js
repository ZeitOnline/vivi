(function() {

MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (! zeit.cms.in_cp_editor()) {
        return;
    }

    zeit.edit.library.create(
        'region', context_url, 'Regionen', '@@region-factories.json');
    zeit.edit.library.create(
        'area', context_url, 'Flächen', '@@area-factories.json');
    zeit.edit.library.create('all', context_url, 'Module');

    zeit.edit.library.tabs.activate('all', /*show_parent=*/false);
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
            return {'block_type': draggable.getAttribute('cms:block_type'),
                    'block_params': draggable.getAttribute('cms:block_params')};
        }
    });

    zeit.edit.drop.registerHandler({
        accept: ['editable-module'],
        activated_by: 'action-cp-module-movable',
        url_attribute: 'cms:move-block-url',
        query_arguments: function(draggable) {
            return {'id': draggable.getAttribute('id')};
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

    zeit.edit.drop.registerHandler({
        accept: ['type-area'],
        activated_by: 'action-cp-region-module-movable',
        url_attribute: 'cms:move-block-url',
        query_arguments: function(draggable) {
            return {'id': draggable.getAttribute('id')};
        }
    });

    zeit.edit.drop.registerHandler({
        accept: ['body-module'],
        activated_by: 'action-cp-body-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type'),
                    'block_params': draggable.getAttribute('cms:block_params')};
        }
    });

    zeit.edit.drop.registerHandler({
        accept: ['type-region'],
        activated_by: 'action-cp-type-region-movable',
        url_attribute: 'cms:move-block-url',
        query_arguments: function(draggable) {
            return {'id': draggable.getAttribute('id')};
        }
    });

});

}());
