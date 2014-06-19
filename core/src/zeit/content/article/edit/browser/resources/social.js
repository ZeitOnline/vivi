(function($) {

$(document).bind('fragment-ready', function(event) {
    $('input#social\\.short_text', event.__target).unbind(
    'change.zeit.article.social.short_text').bind(
        'change.zeit.article.social.short_text', function(event) {
            var input = $(event.target);
            var limit = input.attr('cms:charlimit');
            var text = input.val();
            if (text.length > limit) {
                input.val(text.substring(0, limit - 3) + '...');
            }
    });

});
}(jQuery));
