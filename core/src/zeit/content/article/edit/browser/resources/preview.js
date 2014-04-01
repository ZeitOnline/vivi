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

        self.tabs.on('tabsactivate', function(event, ui) {
            var id = '#' + $(ui.newPanel).attr('id');
            self.save_selection(id);
            self.reload_frame(id);
        });

        $('#edit-form-article-content').on('fold',function(e,folded){
            if (!folded){
                var id = window.sessionStorage.getItem(self.SESSION_KEY);
                if ($(id).css('height')=="500px"){
                    $(id).data('reloaded',false);
                    self.reload_frame(id);
                }
            }
        });
    },

    reload_frame: function(id) {
        if (!$(id).data('reloaded')){
            $(id).data('reloaded',true);
            $(id).attr("src", $(id).attr("src"));
        }
    },

    save_selection: function(id) {
        var self = this;
        window.sessionStorage.setItem(self.SESSION_KEY, id);
    },

    restore_selection: function() {
        var self = this;
        var id = window.sessionStorage.getItem(self.SESSION_KEY);
        if (! id) {
            id = '#preview-tablet';
        }
        $(id).data('reloaded',true);
        self.tabs.tabs('option', 'active', $(id).index());
    }

});


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if ($('#preview-tabs').length) {

        var preview_tabs = new zeit.content.article.PreviewTabs('#preview-tabs');

        window.addEventListener("message", function(e){
            var id =  e.data.tablet ? "#preview-tablet" : "#preview-full";
            if (! e.data.height_obj) {
                return;
            }
            var height = e.data.height_obj.offsetHeight;
            if (height >= 500){
               $(id).css('height',(height+20)+"px");
            }
        }, false);
    }
});

})(jQuery);
