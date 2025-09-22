(function($) {
"use strict";

zeit.cms.declare_namespace('zeit.content.image');

zeit.content.image.parse_mdb_drop = function (transfer) {
    const data = JSON.parse(transfer.getData('text/plain'));
    return data['data'].map(mdb_id => {
        const file_name = data['href_map'][mdb_id].replace(/^.*&linkfile=(.+)\.IRZEIT[^.]+(\..+)&file.*$/, '$1$2');
        const thumb_path = data['thumb_map'][mdb_id];
        return {
            mdb_id,
            file_name,
            thumb: (thumb_path.includes(".IRZEITDEV_") ? 'https://cms-dev.interred.zeit.de' : 'https://cms.interred.zeit.de') + thumb_path
        };
    });
};

zeit.content.image.get_mdb_metadata = function (mdb_id) {
    return new Promise((resolve, reject) => {
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: window.application_url + '/@@mdb_metadata',
            data: {'id':  mdb_id},
            success: resolve,
            error: request => reject(request.responseText)
        });
    });
};

zeit.content.image.DropMDBWidget = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        element = $(document.getElementById(element));
        self.landingzone = $('.landing-zone-candidate', element);
        self.input = $('input[type="hidden"]', element);
        self.id_input = $('input[type="text"]', element);
        self.id_button = $('button', element);
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
                ({mdb_id} = zeit.content.image.parse_mdb_drop(transfer)[0]);
            } catch (error) {
                log(error);
                return;
            }
            self.retrieve(mdb_id);
        });

        self.id_button.on('click', function(e) {
            self.retrieve(self.id_input.val());
        });
    },

    _accept_drag: function(data) {
        // The actual data is not available except in the drop event (apparently
        // this is by design), so we use a kludgy heuristic instead.
        return MochiKit.Base.arrayEqual(
            data.types.toSorted(), ['application/json', 'text/html', 'text/plain']);
    },

    retrieve: function(mdb_id) {
        zeit.content.image.get_mdb_metadata(mdb_id).then(data => this.set(data)).catch(e => {
            log(e);
            alert(e);
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
