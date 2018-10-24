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

    var update_copyright_visibility = function() {
        // Toggle copyright fields, depending on image company choice.
        var copyrights = $('.fieldname-copyrights .combinationFieldWidget');
        copyrights.each(function(index) {
            // Image company is determinded by select widget.
            var photographer = '#form\\.copyrights\\.' + index + '\\.\\.combination_00';
            var company = $('#form\\.copyrights\\.' + index + '\\.\\.combination_01 option:selected');
            var custom_company = '#form\\.copyrights\\.' + index + '\\.\\.combination_02';
            if (company.text() == 'keine Agentur') {
                // Hide photographer in case there is no company selected.
                $(photographer).closest('tr').css('visibility', 'hidden');
                // Clear to prevent values in both fields.
                $(photographer).val('');
                $(custom_company).closest('tr').css('visibility', 'visible');
            } else {
                // Hide custom company in case there is an company selected.
                $(custom_company).closest('tr').css('visibility', 'hidden');
                // Clear first, to prevent values in both fields.
                $(custom_company).val('');
                $(photographer).closest('tr').css('visibility', 'visible');
            }
        });
    };

    $(document).ready(function() {
        if (!$('fieldset.image-form').length) {
            return;
        }

        var dynamic_widgets = {
            '.fieldname-display_type .widget': update_origin_visibility,
            '.fieldname-copyrights .combinationFieldWidget': update_copyright_visibility,
        };

        // update visibility on change, unless we are in read-only mode
        for (const widget in dynamic_widgets) {
            // set initial visibility on load
            dynamic_widgets[widget]();

            if ($(widget).find('select').length) {
                $(widget).find('select').on('change', function() {
                    dynamic_widgets[widget]();
                });
            }
        }
    });

})();
