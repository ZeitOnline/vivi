(function($) {

zeit.cms.declare_namespace('zeit.content.article');


zeit.content.article.PreviewTabs = gocept.Class.extend({

    SESSION_KEY: 'zeit.content.article.preview.selected',

    construct: function(id) {
        var self = this;
        self.initialize_tabs(id);
        self.restore_selection();
    },

    initialize_tabs: function(id) {
        var self = this;
        self.tabs = $(id).tabs();
        $(id)[0].preview_tab = self;
        self.tabs.tabs('add', '#preview-tablet', 'iPad');
        self.tabs.tabs('add', '#preview-full', 'Desktop');

        self.tabs.bind('tabsselect', function(event, ui) {
            var id = $(ui.tab).attr('href');
            self.save_selection(id);
        });
    },

    save_selection: function(id) {
        var self = this;
        window.sessionStorage.setItem(self.SESSION_KEY, id);
    },

    restore_selection: function() {
        var self = this;
        var id = window.sessionStorage.getItem(self.SESSION_KEY);
        self.tabs.tabs('select', id);
    }

});


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if ($('#preview-tabs').length) {
        new zeit.content.article.PreviewTabs('#preview-tabs');
    }
});

})(jQuery);
