(function($){

var check_char_limit = function(target, span, warning, limit) {
    var count = target.val().length;
    var label = count + '/' + limit;
    if ((limit - count) < 0) {
        span.css("color", "#900").html(label);
        target.addClass('error');
    } else if (warning && (warning - count) < 0) {
        span.css("color", "#ffa500").html(label);
        target.removeClass('error');
    } else {
        span.css("color", "#006622").html(label);
        target.removeClass('error');
    }
};

$.fn.limitedInput = function() {
    return this.each(function() {
        var area = $(this);
        var limit = area.attr('cms:charlimit');
        var warning = area.attr('cms:charwarning');
        var container = area.closest('.widget');
        var span = $('<span />').addClass('charlimit');
        container.append(span);
        check_char_limit(area, span, warning, limit);
        area.bind("keyup focus blur", function(event) {
            check_char_limit($(event.target), span, warning, limit);
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
