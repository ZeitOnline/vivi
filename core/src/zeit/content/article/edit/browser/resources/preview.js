(function($) {

zeit.cms.declare_namespace('zeit.content.article');


zeit.content.article.PreviewTabs = gocept.Class.extend({

    construct: function(id) {
        self.tabs = $(id).tabs();
        $(id)[0].preview_tab = self;
        self.tabs.tabs('add', '#preview-tablet', 'iPad');
        self.tabs.tabs('add', '#preview-full', 'Desktop');
    }

});


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    new zeit.content.article.PreviewTabs('#preview-tabs');
});

})(jQuery);
