(function($) {

zeit.cms.normalize_filename = function(filename) {
    var result = filename;
    result = result.trim().toLowerCase();
    result = result.replace(/ä/g, 'ae');
    result = result.replace(/ö/g, 'oe');
    result = result.replace(/ü/g, 'ue');
    result = result.replace(/ß/g, 'ss');

    // Remove all special characters, but keep dots for special treatment
    result = result.replace(/(.*?)([^a-z0-9.]+)$/, '$1');
    result = result.replace(/[^a-z0-9.]/g, '-');
    // Save the last dot (so filename extensions are not destroyed)
    result = result.replace(/(.*)\.(.*?)/, '$1_$2');
    // Remove all dots
    result = result.replace(/\./g, '-');
    // Restore last dot
    result = result.replace(/_/, '.');

    // Collapse multiple consecutive dashes
    result = result.replace(/-+/g, '-');
    return result;
};


$(document).ready(function() {
    $('form:not([action$="zeit.content.link.Add"]) #form\\.__name__').bind(
        'change', function() {
        var input = $(this);
        input.val(zeit.cms.normalize_filename(input.val()));
    });
});

}(jQuery));
