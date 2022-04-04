(function($){

var copy_to = function(target) {
    return function() {
        var src = $(this).val();
        if ((! $(target).val()) &&
            (target != '#social\\.short_text' ||
            $('#metadata-genre\\.genre option:selected').text() == 'Nachricht')) {
                $(target).val(src).focusout();
                text_color();
        }
    };
};

$(document).bind('fragment-ready', function(event) {
    $('#teaser-supertitle\\.teaserSupertitle', event.__target).bind(
        'change', copy_to('#article-content-head\\.supertitle'));

    $('#teaser-title\\.teaserTitle', event.__target).bind(
        'change', copy_to('#article-content-head\\.title'));

    $('#teaser-text\\.teaserText', event.__target).bind(
        'change', copy_to('#article-content-head\\.subtitle'));

    $('#teaser-text\\.teaserText', event.__target).bind(
        'change', copy_to('#social\\.short_text'));
});

}(jQuery));
