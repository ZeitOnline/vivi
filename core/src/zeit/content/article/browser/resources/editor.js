(function() {

zeit.cms.declare_namespace('zeit.content.article');


var ident = MochiKit.Signal.connect(
    zeit.edit.editor, 'script-loading-finished',
    function() {
        MochiKit.Signal.disconnect(ident);

    zeit.content.article.body_sorter = new zeit.edit.sortable.BlockSorter(
        'editable-body');
    });

})();
