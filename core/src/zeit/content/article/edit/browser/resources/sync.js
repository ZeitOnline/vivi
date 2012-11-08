(function($){

$(document).bind('fragment-ready', function(event) {
    $('#teaser-supertitle\\.teaserSupertitle', event.__target).bind(
        'change', function(){
            var value = $(this).val();
            $('#article-content-head\\.supertitle').val(value).focusout();
        });
});

}(jQuery));
