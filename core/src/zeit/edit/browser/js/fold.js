(function(){

zeit.cms.declare_namespace('zeit.edit');


zeit.edit.FoldBlock = function(context) {
    var id = context.getAttribute('href');
    zeit.edit.toggle_folded(id);
};

zeit.edit.toggle_folded = function(id) {
    MochiKit.DOM.toggleElementClass('folded', id);
    window.sessionStorage.setItem(
        'folding.' + id,
        JSON.stringify(MochiKit.DOM.hasElementClass(id, 'folded')));
};

zeit.edit.restore_folding = function() {
    forEach(
        $$('a[cms:cp-module="zeit.edit.FoldBlock"]'),
        function(action) {
            var id = action.getAttribute('href');
            var state = window.sessionStorage.getItem('folding.' + id);
            if (state === null) {
                return;
            }
            state = JSON.parse(state);
            if (state) {
                log("Restore folding=on for", id);
                MochiKit.DOM.addElementClass(id, 'folded');
            } else {
                log("Restore folding=off for", id);
                MochiKit.DOM.removeElementClass(id, 'folded');
            }
    });
};


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
        zeit.edit.restore_folding();
    });
});

})();
