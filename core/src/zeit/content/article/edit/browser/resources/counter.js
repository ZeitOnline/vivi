(function($){

$.fn.limitedInput = function() {
    return this.each(function() {
        var area = $(this);
        var container = area.closest('.widget');
        var limit = area.attr('cms:charlimit');
        var count = area.val().length || 0;
        var suffix = '/' + limit;
        var label = count + suffix;
        var span = $('<span />').addClass('charlimit').html(label);
        container.append(span);
        area.bind("keyup focus blur onload", function (e) {
            var count = $(e.target).val().length;
            var label = count + suffix;
            if ((limit - count) < 0) {
                span.css("color", "#900").html(label);
            } else {
                span.css("color", "#000").html(label);
            }
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
