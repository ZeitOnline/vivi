(function($) {

zeit.cms.declare_namespace('zeit.newsletter');

MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    zeit.newsletter.group_sorter = new zeit.edit.sortable.BlockSorter(
        'newsletter_body');
});

})(jQuery);