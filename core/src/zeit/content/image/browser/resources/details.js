// Copyright (c) 2012 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {

$(document).bind('fragment-ready', function(event) {
    $('.image_details button.toggle_infos', event.__target).bind(
        'click', function(event) {
        var button = $(event.target);
        var pane = $('.picture_information', button.closest('.image_details'));
        pane.slideToggle('slow');
        return false;
    });
});

}(jQuery));