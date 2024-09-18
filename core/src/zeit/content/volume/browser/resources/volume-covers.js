(function($) {

$(document).bind('fragment-ready', function(event) {

    if (! Boolean($('body.type-volume.location-workingcopy').length)) {
        return;
    }
    // Check first if a choose cover element already exists, because part
    // of the DOM is refreshed, if a cover is added.
    if ($('#choose-cover').length > 0) {
        return;
    }
    // XXX We might want to use a more specific selector than just
    // ".column-right" and take the fieldnames into account (would have to be a
    // substring match on "fieldname-cover*", so it might be complicated).
    $('fieldset.column-right').first().before(
        '<fieldset class="column-right choose">' +
        '<legend>COVERS</legend> <select id="choose-cover">' +
        '</select></fieldset>');

    // Iterate through all legends and add them to the select
    // ignoring the first legend, because it is the legend for the selection
    $('fieldset.column-right legend:not(:first)').each(function(i, element) {
        $('#choose-cover').append(
            '<option>' + $(element).text() + '</option>');
    });

    var choose_cover = $('#choose-cover');
    choose_cover.on('change', function(event) {
        show_fieldsets(this.value);
    });
    // Show only one product, when the page is loaded
    choose_cover.trigger('change');
});

var show_fieldsets = function(selected_text) {
    $('fieldset.column-right').each(function(i, element) {
        element = $(this);
        if (element.hasClass('choose')) {
            return;
        }
        if (element.find('legend').first().text() == selected_text) {
            element.show();
        } else {
            element.hide();
        }
    });
};

}(jQuery));
