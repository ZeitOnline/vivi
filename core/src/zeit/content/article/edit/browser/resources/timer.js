(function($){

function print_timestamp(element) {
    $(element).text(new Date().strftime('%d.%m.%Y %H:%Mh'));
}

$.fn.timer = function() {
    var jq_elements = this;
    return jq_elements.each(function() {
        var element = this;
        if (element.timer !== undefined) {
            return;
        }
        element.timer = window.setInterval(print_timestamp, 1000, element);
    });
};


$(document).bind('fragment-ready', function(event) {
    $('.timer', event.__target).timer();
});

}(jQuery));
