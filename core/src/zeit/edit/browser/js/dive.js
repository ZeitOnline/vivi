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

    /*
     * Nasty hack in order to prevent divers from instantly closing after
     * changing any value inside the diver's widgets.
     * This is caused due to rerendering the diver after storing a new value.
     */
    (function($) {

        if ( window.memo_visible == true ) {
            $("#memo-diver").show();
        } else if ( window.options_visible == true ) {
            $("#options-diver").show();
        }

    }(jQuery));

});


(function($){

    $.fn.createFoldBoxes = function() {
        var self = $(this);

        // Create checkboxes for each foldable edit area.
        $('.editable-area > .edit-bar').each(function() {
            var span    = $(this).children('span:first').text();
            var id      = $(this).parent().attr('id');
            var fset    = self.children('fieldset');
            var storage = sessionStorage['folding.' + id];
            var widget  = jQuery('<div/>', {
                class: 'widget',
            }).appendTo(fset);
            jQuery('<input/>', {
                checked: storage ? '' : 'checked',
                class: 'fold-checker',
                name: id,
                type: 'checkbox',
            }).appendTo(widget);
            jQuery('<label/>').text(span).appendTo(widget);
        });

        $('input.fold-checker').click(function() {
            var id = $(this).attr('name');
            sessionStorage['folding.' + id] =
              sessionStorage['folding.' + id] ? '' : 'checked';
        });
    };

})(jQuery);

})();
