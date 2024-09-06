(function ($) {

var FIELDS = {
    'centerpage': 'referenced_cp',
    'custom': 'query',
    'topicpage': 'referenced_topicpage',
    'elasticsearch-query': 'elasticsearch_raw_query',
    'reach': 'reach_service',
    'related-topics': 'related_topicpage',
    'topicpagelist': 'topicpagelist_order',
    'rss-feed': 'rss_feed',
    'sql-query': 'sql_query'
};


var show_matching_fieldset = function(container, current_type) {
    $(Object.keys(FIELDS)).each(
        function(i, key) {
            var field = FIELDS[key];
            var method = field == FIELDS[current_type] ? 'show' : 'hide';
            var target = $('.fieldname-' + field, container).closest('fieldset');
            target[method]();
    });
};

var enable_autopilot = function(container) {
    $('.fieldname-automatic .checkboxType', container).prop('checked', true);
};

var hide_hide_dupes_checkbox_for_reach = function(container, current_type) {
    if (current_type === 'reach') {
        $('.fieldname-hide_dupes', container).hide();
    } else {
        $('.fieldname-hide_dupes', container).show();
    }
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

    show_matching_fieldset(event.__target, type_select.val());
    hide_hide_dupes_checkbox_for_reach(event.__target, type_select.val());
    type_select.on(
        'change', function() {
            var value = $(this).val();
            show_matching_fieldset(event.__target, value);
            enable_autopilot(event.__target);
            hide_hide_dupes_checkbox_for_reach(event.__target, value);
    });
});

$(document).bind('fragment-ready', function(event) {
    $('.fieldname-query select[id$="combination_00"]', event.__target).on(
        'change', function() {
            $(this).closest('form').trigger('submit');
    });
});

}(jQuery));
