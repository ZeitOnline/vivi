(function($) {
"use strict";

$(document).ready(function() {
    $('#workingcopycontents .draggable-content').each(function(i, element) {
        zeit.cms.createDraggableContentObject(element);
    });
});

})(jQuery);
