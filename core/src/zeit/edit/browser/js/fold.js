(function(){

zeit.cms.declare_namespace('zeit.edit');


zeit.edit.FoldBlock = gocept.Class.extend({

    construct: function(context) {
        var self = this;
        var id = context.getAttribute('href');
        MochiKit.DOM.toggleElementClass('folded', id);
    },

    // @staticmethod
    restore_folding: function() {
        forEach(
            $$('a[cms:cp-module="zeit.edit.FoldBlock"]'),
            function(action) {
                var id = action.getAttribute('href');
                if (sessionStorage['folding.' + id]) {
                    log("Restore folding=on for", id);
                    MochiKit.DOM.addElementClass(id, 'folded');
                } else {
                    log("Restore folding=off for", id);
                    MochiKit.DOM.removeElementClass(id, 'folded');
                }
        });
    }

});

MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {
        zeit.edit.FoldBlock.prototype.restore_folding();
});

}());
