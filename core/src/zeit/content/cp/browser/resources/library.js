(function() {

MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {

    zeit.edit.library.create('all', context_url, 'Alle');
    zeit.edit.library.create_for_element('lead', 'Aufmacher');
    zeit.edit.library.create_for_element('informatives', 'Informatives');
    zeit.edit.library.create_for_element('teaser-mosaic', 'Mosaic');

});

zeit.edit.drop.registerHandler({
    accept: ['lead-module'],
    activated_by: 'action-lead-module-droppable',
    url_attribute: 'cms:create-block-url',
    query_arguments: function(draggable) {
        return {'block_type': draggable.getAttribute('cms:block_type')};
    },
});

zeit.edit.drop.registerHandler({
    accept: ['informatives-module'],
    activated_by: 'action-informatives-module-droppable',
    url_attribute: 'cms:create-block-url',
    query_arguments: function(draggable) {
        return {'block_type': draggable.getAttribute('cms:block_type')};
    },
});

zeit.edit.drop.registerHandler({
    accept: ['teaser-mosaic-module'],
    activated_by: 'action-teaser-mosaic-module-droppable',
    url_attribute: 'cms:create-block-url',
    query_arguments: function(draggable) {
        return {'block_type': draggable.getAttribute('cms:block_type')};
    },
});


})();
