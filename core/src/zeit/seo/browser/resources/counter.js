(function($){

$(document).ready(function() {
    if (!$('form[action$="seo-edit.html"]').length) {
        return;
    }

    $('#form\\.html_title').countedInput();
    $('#form\\.html_description').countedInput();

});

}(jQuery));
