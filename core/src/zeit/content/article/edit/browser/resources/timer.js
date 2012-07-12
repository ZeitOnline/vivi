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


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    MochiKit.Signal.connect(zeit.cms.SubPageForm, 'after-reload', function() {
        $('.timer').timer();
    });
});

}(jQuery));
