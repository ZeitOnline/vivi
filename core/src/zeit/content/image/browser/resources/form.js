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
        // Image company is determinded by select widget.
        var photographer = $('#form\\.copyright\\.combination_00');
        var photographer_tr = photographer.closest('tr');
        var company = $('#form\\.copyright\\.combination_01 option:selected');
        var company_tr = company.closest('tr');
        var custom_company = $('#form\\.copyright\\.combination_02');
        var custom_company_tr = custom_company.closest('tr');

        // We need to place company above photographer here, because it's not
        // viable to do so in the model layer.
        company_tr.insertBefore(photographer_tr);

        if (company.text() == 'Andere') {
            // Hide photographer in case there is no company selected.
            photographer_tr.hide();
            // Clear to prevent values in both fields.
            photographer.val('');
            custom_company_tr.show();
        } else {
            // Hide custom company in case there is an company selected.
            custom_company_tr.hide();
            // Clear first, to prevent values in both fields.
            custom_company.val('');
            photographer_tr.show();
        }
    };

    var bind_function_to_select_change = function (selector, func) {
        // set initial visibility on load
        func();
        // update visibility on change, unless we are in read-only mode
        if ($(selector).find('select').length) {
            $(selector).find('select').on('change', function() {
                func();
            });
        }
    };

    $(document).ready(function() {
        if (!$('fieldset.image-form').length) {
            return;
        }
        bind_function_to_select_change('.fieldname-copyright .combinationFieldWidget',
            update_copyright_visibility);
        bind_function_to_select_change('.fieldname-display_type .widget',
            update_origin_visibility);
    });
})();
