(function($) {

// The actual visibility toggle is done by zeit.cms:details.js
// idempotent bind, see http://stackoverflow.com/a/12322655/1885340
$(document).bind('fragment-ready', function(event) {
    $('button.toggle_infos', event.__target).unbind(
    'click.zeit.article.keywords').bind(
        'click.zeit.article.keywords', function(event) {
        var button = $(event.target);
        var current_caption = button.text();
        button.text(button.data('caption'));
        button.data('caption', current_caption);
        return false;
    });
});

}(jQuery));
