/*global document,window,MochiKit,gocept,zeit,log*/
(function($) {
"use strict";

zeit.cms.declare_namespace('zeit.content.image');

zeit.content.image.DropMDBWidget = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        element = $(document.getElementById(element));
        self.landingzone = $('.landing-zone-candidate', element);

        element.on('dragenter', function(e) {
            if (self._accept_drag(e.originalEvent.dataTransfer)) {
                self.landingzone.addClass('droppable-active');
            }
        });
        element.on('dragleave', function(e) {
            self.landingzone.removeClass('droppable-active');
        });
        element.on('dragover', function(e) {
            e.originalEvent.dataTransfer.dropEffect = 'move';
            e.preventDefault();  // necessary to make drop work
        });
        element.on('drop', function(e) {
            e.stopPropagation();
            e.preventDefault();
            self.landingzone.removeClass('droppable-active');
            if (! self._accept_drag(e.originalEvent.dataTransfer)) {
                return;
            }
            try {
                var data = JSON.parse(
                    e.originalEvent.dataTransfer.getData('text/plain'));
                var mdb_id = data['data'][0];
            } catch (e) {
                log(e);
                return;
            }
            self.set(mdb_id);
        });
    },

    _accept_drag: function(data) {
        // The actual data is not available except in the drop event (apparently
        // this is by design), so we use a kludgy heuristic instead.
        return MochiKit.Base.arrayEqual(
            data.types, ['text/plain', 'application/json']);
    },

    set: function(mdb_id) {
        var self = this;
        $('#form\\.mdb_blob').val(mdb_id);
    }

});

})(window.jQuery);
