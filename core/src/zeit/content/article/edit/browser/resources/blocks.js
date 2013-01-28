(function($) {

    MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
        if (!zeit.cms.in_article_editor()) {
            return;
        }

        MochiKit.Signal.connect(zeit.edit.editor, 'added', function(block_id) {
            var current = $('#'+block_id);
            if (!current.hasClass('type-division')) {
                return;
            }
            $('input.textType', current).focus();
        });

    });

})(jQuery);
