/*global document,window,MochiKit,gocept,zeit,log*/
(function($) {
"use strict";

zeit.cms.declare_namespace('zeit.content.image');

zeit.content.image.DropMDBWidget = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        element = $(document.getElementById(element));
        self.landingzone = $('.landing-zone-candidate', element);
        self.input = $('input', element);
        element[0].widget = self;  // for tests

        element.on('dragenter', function(e) {
            var transfer = e.originalEvent.dataTransfer;
            if (self._accept_drag(transfer)) {
                self.landingzone.addClass('droppable-active');
            }
        });
        element.on('dragleave', function(e) {
            self.landingzone.removeClass('droppable-active');
        });
        element.on('dragover', function(e) {
            var transfer = e.originalEvent.dataTransfer;
            transfer.dropEffect = 'move';
            e.preventDefault();  // necessary to make drop work
        });
        element.on('drop', function(e) {
            e.stopPropagation();
            e.preventDefault();
            self.landingzone.removeClass('droppable-active');
            var transfer = e.originalEvent.dataTransfer;
            if (! self._accept_drag(transfer)) {
                return;
            }
            var mdb_id;
            try {
                var data = JSON.parse(transfer.getData('text/plain'));
                mdb_id = data['data'][0];
            } catch (error) {
                log(error);
                return;
            }
            self.retrieve(mdb_id);
        });
    },

    _accept_drag: function(data) {
        // The actual data is not available except in the drop event (apparently
        // this is by design), so we use a kludgy heuristic instead.
        return MochiKit.Base.arrayEqual(
            data.types, ['text/plain', 'application/json', 'text/html']);
    },

    retrieve: function(mdb_id) {
        var self = this;
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: window.application_url + '/@@mdb_metadata',
            data: {'id':  mdb_id},
            success: function(data) {
                self.set(data);
            },
            error: function(request) {
                log(request.responseText);
                alert(request.responseText);
            }
        });
    },

    set: function(data) {
        var self = this;

        self.input.val(data['mdb_id']);
        $('#form\\.mdb_id').val(data['mdb_id']);

        var select = $('#form\\.copyright\\.combination_01');
        var other = $('option:contains("Andere")', select).prop(
            'selected', true);
        select.trigger('change');

        var credits = data['credit'];
        if (! credits) {
            credits = data['fotograf'];
        }
        if (! credits) {
            credits = data['rechteinhaber'];
        }
        $('#form\\.copyright\\.combination_02').val(credits);

        $('#form\\.caption').val(data['beschreibung']);
        $('#form\\.release_period\\.combination_01').val(data['expires']);

        self.landingzone.text(self.landingzone.data('success'));
    }

});

})(window.jQuery);
