/*global window,zeit,document*/
(function() {
    "use strict";

    var $ = window.jQuery;

    var get_display_type = function() {
        // In read-only mode the widget contains no select, but the selected
        // option as text.
        var type, widget;
        widget = $('.fieldname-display_type .widget');
        if (widget.find('select').length) {
            type = widget.find('select option:selected').text();
        } else {
            type = widget.text();
        }
        return type;
    };

    var update_origin_visibility = function() {
        // Hide `origin` field unless `display_type` is `Infografik`.
        var type = get_display_type();
        if (type === 'Infografik') {
            $('.fieldname-origin').show();
        } else {
            $('.fieldname-origin').hide();
        }
    };

    $(document).ready(function() {
        if (!$('fieldset.image-form').length) {
            return;
        }

        // set initial visibility on load
        update_origin_visibility();

        // update visibility on change, unless we are in read-only mode
        var widget = $('.fieldname-display_type .widget');
        if (widget.find('select').length) {
            widget.find('select').on('change', function () {
                update_origin_visibility();
            });
        }
    });

})();
