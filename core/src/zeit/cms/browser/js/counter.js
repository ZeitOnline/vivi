(function($){

var check_char_limit = function(target, span, limit) {
    var count = target.val().length;
    var label = count + '/' + limit;
    if ((limit - count) < 0) {
        span.css("color", "#900").html(label);
        target.addClass('error');
    } else {
        span.css("color", "#000").html(label);
        target.removeClass('error');
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
            check_char_limit($(event.target), span, limit);
        });
    });
};

$.fn.countedInput = function() {
    return this.each(function() {
        var area = $(this);
        var container = area.closest('.widget');
        var span = $('<span />').addClass('charlimit');
        container.append(span);
        span.html(area.val().length);
        area.bind("keyup focus blur", function(event) {
            span.html($(event.target).val().length);
        });
    });
};

}(jQuery));
