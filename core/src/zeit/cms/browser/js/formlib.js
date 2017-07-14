(function($){

// zc.form combination widget insists on using this.
// Re-created from ancient JS code in zope.formlib:subpageform.pt
window.toggleFormFieldHelp = function(label,state) {
    var help = $(label).closest('tr').find('.form-fields-help');
    if (state) {
        help.show();
    } else {
        help.hide();
    }
};

$(document).bind('fragment-ready', function(event) {
    $('.form-fields-help', event.__target).hide();
});

$(document).ready(function() {
    $('.form-fields-help').hide();
});

}(jQuery));
