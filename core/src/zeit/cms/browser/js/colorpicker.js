// Copyright (c) 2014 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {

$(document).bind('fragment-ready', function(event) {

    $('.colorpicker-widget', event.__target).each(function(i, elem) {
        $(elem).colorpicker({
            parts: ['map', 'bar', 'swatches', 'hex', 'footer'],
            layout: {
                map: [0, 0, 1, 1],
                bar: [1, 0, 1, 1],
                swatches: [2, 0, 1, 1],
                hex: [0, 1, 1, 1]
            }
        });
    });

});

}(jQuery));
