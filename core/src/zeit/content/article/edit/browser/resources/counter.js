(function($){

$.fn.limitedInput = function(limit) {
    return this.each(function() {
        var self = $(this);
        var container = self.find('.widget:first');
        var area = $('textarea', container);
        var val = area.val().length || 0;
        var span = $('<span />').addClass('charlimit').html(
            (val > 0 ? limit - val : limit) + " Zeichen");
        container.prepend(span);
        area.bind("keyup focus blur", function (e) {
            var count = limit - $(e.target).val().length;
            if (count < 21 && count > 10) {
                span.css("color", "#900").html(count + " Zeichen");
            } else if (count < 11) {
                span.css("color", "#ff0000").html(count + " Zeichen");
            } else {
                span.css("color", "#777").html(count + " Zeichen");
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

    MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
            $('#article-editor-text').countedInput();
    });

});

}(jQuery));
