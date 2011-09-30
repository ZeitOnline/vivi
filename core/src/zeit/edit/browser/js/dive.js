(function(){

MochiKit.Signal.connect(window, 'script-loading-finished', function() {

    (function($) {
        $('#options-diver-button').click(function() {
            if ( $("#memo-diver").filter(":visible").size() > 0 ) {
                $("#memo-diver-button").click();
            }
            $("#options-diver").slideToggle(600, "swing");
            window.options_visible = !window.options_visible
        });

        $('#memo-diver-button').click(function() {
            if ( $("#options-diver").filter(":visible").size() > 0 ) {
                $("#options-diver-button").click();
            }
            $("#memo-diver").slideToggle(600, "swing");
            window.memo_visible = !window.memo_visible
        });
    }(jQuery));

});

MochiKit.Signal.connect(window, 'changed', function() {

    (function($) {
        if ( window.memo_visible == true ) {
            $("#memo-diver").show();
        } else if ( window.options_visible == true ) {
            $("#options-diver").show();
        }
    }(jQuery));

});

})();
