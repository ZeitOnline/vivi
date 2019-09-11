(function ($) {


var show_dependent_field = function(container, current_status) {
    var method = current_status == 'True' ? 'show' : 'hide';
    var target = $('.fieldname-thirdparty_vendors', container);
    target[method]();

};


var setup = function(container) {
    var status_select = $('.fieldname-has_thirdparty select', container);
    show_dependent_field(container, status_select.val());
    status_select.on(
        'change', function() {
            show_dependent_field(container, $(this).val());
        });
};

$(document).bind('fragment-ready', function(event) {
    setup(event.__target);
});

$(document).ready(function() {
    if ($('body').hasClass('location-workingcopy')) {
        setup(document);
    }
});

}(jQuery));
