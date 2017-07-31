(function($) {

var update_title = function(event) {
    var select = $(event.target);
    var form = select.closest('form');
    var input = form.find('.fieldname-mobile_title input');
    $.ajax({
        type: 'GET',
        url: window.application_url + '/@@zeit.push.payload_template_title',
        data: {'q': select.val()},
        success: function(data) {
            input.val(data);
        },
        error: function(request, error) {
            input.val('');
        }
    });
};

$(document).bind('fragment-ready', function(event) {
    $('select#mobile\\.mobile_payload_template', event.__target).unbind(
    'change.zeit.article.mobile.payload_template').bind(
        'change.zeit.article.mobile.payload_template', update_title);

});

$(document).ready(function() {
    $('select#form\\.mobile_payload_template').bind('change', update_title);
});

}(jQuery));
