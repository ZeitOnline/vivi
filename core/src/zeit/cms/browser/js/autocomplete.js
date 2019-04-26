// Copyright (c) 2014 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {

$(document).bind('fragment-ready', function(event) {

    $('.autocomplete-widget', event.__target).each(function(i, elem) {
        $(elem).autocomplete({
            source: $(elem).attr('cms:autocomplete-source'),
            minLength: 3,
            // XXX This might not be an applicable/sensible place in general.
            appendTo: $(elem).closest('form').parent(),
            focus: function(event, ui) {
                $(elem).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                // for zeit.cms.InlineForm
                $(elem).trigger('change');
                $(elem).trigger('focusout');
                return false;
            }
        });
    });

});

}(jQuery));
