(function($) {

$(document).bind('fragment-ready', function(event) {
    $('#new-filename\\.rename_to', event.__target).bind('change', function() {
        var input = $(this);
        input.val(zeit.cms.normalize_filename(input.val()));
    });
});


$(document).ready(function() {
    $('.breakingnews-title').bind('keyup', function() {
        var title = $(this).val();
        var target = '#form\\.__name__';
        $(target).val(title);
        $(target).trigger('change');
    });
});


}(jQuery));
