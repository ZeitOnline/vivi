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
            /^(.*)\.(jpg|jpeg|png|pdf|mp3|swf|rtf|gif|svg|bmp)$/, '$1_$2');
    // Remove all dots
    result = result.replace(/\./g, '-');
    // Restore saved dot
    result = result.replace(/_/, '.');

    // Collapse multiple consecutive dashes
    result = result.replace(/-+/g, '-');

    // Edge case: Remove special char before the filename extension
    result = result.replace(/-\./, '.');

    return result;
};


$(document).ready(function() {
    var excluded = [
        'zeit.cms.repository.file.Add',
        'zeit.content.rawxml.Add',
        'zeit.content.text.Add',
        'zeit.content.text.json.Add'
    ];

    $('form').each(function(index, form) {
        form = $(form);
        var name_input = form.find('#form\\.__name__');
        if (!name_input.length) {
            return;
        }

        var action = form.attr('action');
        for (var i = 0; i < excluded.length; i++) {
            var item = excluded[i];
            if (action.substr(-item.length) == item) {
                return;
            }
        }

        name_input.bind('change', function() {
            var input = $(this);
            input.val(zeit.cms.normalize_filename(input.val()));
        });
    });
});

}(jQuery));
