(function($){

var check_char_limit = function(target, span, limit) {
    var count = $(target).val().length;
    var label = count + '/' + limit;
    if ((limit - count) < 0) {
        span.css("color", "#900").html(label);
    } else {
        span.css("color", "#000").html(label);
    }
};

$.fn.limitedInput = function() {
    return this.each(function() {
        var area = $(this);
        var limit = area.attr('cms:charlimit');
        var container = area.closest('.widget');
        var span = $('<span />').addClass('charlimit');
        container.append(span);
        check_char_limit(area, span, limit);
        area.bind("keyup focus blur", function(event) {
            check_char_limit(event.target, span, limit);
        });
    });
};

$.fn.countedInput = function() {
    var self = $(this);
    var count = function() {
        var l = self.find('.editable').children().text().length || 0;
        var container = self.parent();
        container.find('.charcount').html(l + " Zeichen");
        if(l > 5000) {
          container.find('.charcount').addClass('charalert');
        } else {
          container.find('.charcount').removeClass('charalert');
        }
    };
    self.bind('keyup', count);
    count();
};


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    $('#article-editor-text').countedInput();
});

$(document).bind('fragment-ready', function(event) {
    $('[cms\\:charlimit]', event.__target).limitedInput();
});

}(jQuery));
