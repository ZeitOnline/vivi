(function ($) {

var FIELDS = {
    'centerpage': 'referenced_cp',
    'custom': 'query',
    'topicpage': 'referenced_topicpage',
    'elasticsearch-query': 'elasticsearch_raw_query',
    'rss-feed': 'rss_feed'
};


var show_matching_field = function(container, current_type) {
    $(Object.keys(FIELDS)).each(
        function(i, key) {
            var field = FIELDS[key];
            var method = field == FIELDS[current_type] ? 'show' : 'hide';
            var target = $('.fieldname-' + field, container).closest('fieldset');
            target[method]();
    });
};


$(document).bind('fragment-ready', function(event) {
    var type_select = $('.fieldname-automatic_type select', event.__target);
    if (! type_select.length) {
        return;
    }

    var fieldsets = event.__target.getElementsByTagName('fieldset');
    if (fieldsets.length > 0) {
        var fieldset_topicbox_id = fieldsets[0].id;
        if (fieldset_topicbox_id !== undefined) {
            if (fieldset_topicbox_id.indexOf('form-topicbox.id-') > -1) {
                return;
            }
        }
    }

    show_matching_field(event.__target, type_select.val());
    type_select.on(
        'change', function() {
            show_matching_field(event.__target, $(this).val());
    });
});

$(document).bind('fragment-ready', function(event) {
    $('.fieldname-query select[id$="combination_00"]', event.__target).on(
        'change', function() {
            $(this).closest('form').trigger('submit');
    });
});

}(jQuery));
