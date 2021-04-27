function display_elements(selected_automatic_type) {

    var cssClass = '.type-article #edit-form-article-content .fieldname-';
    var cssClasses = [];

    var classes = [
        'referenced_cp',
        'referenced_topicpage',
        'topicpage_filter',
        'elasticsearch_raw_query',
        'elasticsearch_raw_order',
        'preconfigured_query',
    ];

    selected_automatic_type = selected_automatic_type.toLowerCase();

    switch (selected_automatic_type) {
        case 'klassisch':
            hide_references(false);
            break;
        case 'centerpage':
            cssClasses.push('referenced_cp');
            break;
        case 'themenseite':
            cssClasses.push('referenced_topicpage');
            cssClasses.push('topicpage_filter');
            break;
        case 'es-query':
            cssClasses.push('elasticsearch_raw_query');
            cssClasses.push('elasticsearch_raw_order');
            break;
        case 'related-api':
            cssClasses.push('topicpage_filter');
            break;
        case 'konfigurationsdatei':
            cssClasses.push('preconfigured_query');
            break;
        default:
            break;
    }

    if (selected_automatic_type != 'klassisch') {
        hide_references(true);
    }

    classes.forEach((cls) => {
        var el = document.querySelectorAll(cssClass + cls);
        if (el.length > 0) {
            el[0].style.display = 'none';
        }
    });

    cssClasses.forEach((cls) => {
        var el = document.querySelectorAll(cssClass + cls);
        if (el.length > 0) {
            el[0].style.display = 'block';
        }
    });
}

function hide_references(hide) {
    var cssClassReferences = "[class*='fieldname-NAME_reference']";
    ['first', 'second', 'third'].forEach((ref) => {
        var reference = document.querySelectorAll(cssClassReferences.replace('NAME', ref));
        if (reference.length > 0) {
            reference[0].style.display = hide ? 'none' : 'block';
        }
    });
}

function eval_automatic_type(el) {
    if (el.length > 0) {
        var sel_val = el[0].selectedOptions[0].text;
        display_elements(sel_val);
    }
}

(function ($) {
    $(document).bind('fragment-ready', function(e) {
        var current_automatic_type_value = document.querySelectorAll('[id$=automatic_type]');
            if (current_automatic_type_value.length > 0) {
                current_automatic_type_value.forEach((el) => {
                    if(el.id.startsWith('topicbox.id') && el.id.endsWith('automatic_type')) {
                        var val = el.selectedOptions[0].text;
                    display_elements(val);
                    return;
                }
            });
        }
        return;
    });

    $(document).bind('change', function(e) {
        if (e.target && e.target.id.indexOf('automatic_type') > -1) {
            var val = document.getElementById(e.target.id);
            if (val == undefined) {
                return;
            }
            val = val.selectedOptions[0].text;
            display_elements(val);
        }
    });
 }(jQuery));
