(function($) {

zeit.cms.normalize_filename = function(filename) {
    var result = filename;
    result = result.trim().toLowerCase();
    result = result.replace(/ä/g, 'ae');
    result = result.replace(/ö/g, 'oe');
    result = result.replace(/ü/g, 'ue');
    result = result.replace(/ß/g, 'ss');

    // Remove special characters at beginning and end
    // XXX It's unclear why this doesn't work as a single regexp.
    result = result.replace(/^([^a-z0-9]+)(.*?)$/, '$2');
    result = result.replace(/^(.*?)([^a-z0-9]+)$/, '$1');
    // Replace special characters, but keep dots for special treatment
    result = result.replace(/[^a-z0-9.]/g, '-');
    // Save dot of filename extensions
    result = result.replace(
            /^(.*)\.(jpg|png|pdf|mp3|swf|rtf|gif|svg|bmp)$/, '$1_$2');
    // Remove all dots
    result = result.replace(/\./g, '-');
    // Restore saved dot
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
