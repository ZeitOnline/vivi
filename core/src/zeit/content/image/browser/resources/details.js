// Copyright (c) 2012 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {

// idempotent bind, see http://stackoverflow.com/a/12322655/1885340
$(document).bind('fragment-ready', function(event) {
    $('.image_details button.toggle_infos', event.__target).unbind(
    'click.zeit.content.image.details').bind(
        'click.zeit.content.image.details', function(event) {
        var button = $(event.target);
        var pane = $('.picture_information', button.closest('.image_details'));
        pane.slideToggle('slow');
        button.toggleClass('folded');
        return false;
    });
});

}(jQuery));
