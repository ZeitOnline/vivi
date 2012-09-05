(function($){

zeit.cms.declare_namespace('zeit.edit');


zeit.edit.fold = function(context) {
    var id = context.getAttribute('href');
    zeit.edit.toggle_folded(id);
};

zeit.edit.toggle_folded = function(id) {
    $('#'+id).toggleClass('folded');
    window.sessionStorage.setItem(
        'folding.' + id, JSON.stringify($('#'+id).hasClass('folded')));
};

zeit.edit.restore_folding = function() {
    $('a[cms\\:cp-module="zeit.edit.fold"]').each(
        function(index, action) {
            var id = action.getAttribute('href');
            var state = window.sessionStorage.getItem('folding.' + id);
            if (state === null) {
                return;
            }
            state = JSON.parse(state);
            if (state) {
                log("Restore folding=on for", id);
                $('#'+id).addClass('folded');
            } else {
                log("Restore folding=off for", id);
                $('#'+id).removeClass('folded');
            }
    });
};


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
        zeit.edit.restore_folding();
    });
});

})(jQuery);
