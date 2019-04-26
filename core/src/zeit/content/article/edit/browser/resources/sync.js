(function($){

var copy_to = function(target) {
    return function() {
        var src = $(this).val();
        if (! $(target).val()) {
            $(target).val(src).focusout();
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
});

}(jQuery));
