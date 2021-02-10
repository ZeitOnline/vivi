function display_elements(selected_source_type) {

    var cssClass = '.type-article #edit-form-article-content .fieldname-';
    var cssClasses = [];

    var classes = [
        'centerpage',
        'topicpage',
        'topicpage_filter',
        'elasticsearch_raw_query',
        'elasticsearch_raw_order',
        'config_query',
    ];

    var selected_source_type = selected_source_type.toLowerCase();

    switch (selected_source_type) {
        case 'manuell':
            hide_references(false);
            break;
        case 'centerpage':
            cssClasses.push('centerpage');
            break;
        case 'tms-themenseite':
            cssClasses.push('topicpage');
            cssClasses.push('topicpage_filter');
            break;
        case 'es-query':
            cssClasses.push('elasticsearch_raw_query');
            cssClasses.push('elasticsearch_raw_order');
            break;
        case 'tms-related-api':
            cssClasses.push('topicpage_filter');
            break;
        case 'config-query':
            cssClasses.push('config_query')
            break;
        default:
            break;
    }

    if (selected_source_type != 'manuell') {
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

function eval_source_type(el) {
    if (el.length > 0) {
        var sel_val = el[0].selectedOptions[0].text;
        display_elements(sel_val);
    }
}

document.addEventListener('change', (e) => {
    if (e.target && e.target.id.indexOf('source_type') > -1) {
        var val = document.getElementById(e.target.id);
        if (val == undefined) {
            return;
        }
        val = val.selectedOptions[0].text;

        display_elements(val);
    }
});
