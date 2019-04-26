(function($){

$.fn.countedEditableInput = function() {
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
    $('#article-editor-text').countedEditableInput();
});

$(document).bind('fragment-ready', function(event) {
    $('[cms\\:charlimit]', event.__target).limitedInput();
});

$(document).ready(function() {
    $('[cms\\:charlimit]').limitedInput();
});

}(jQuery));
