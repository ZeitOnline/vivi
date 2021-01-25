function display_elements(selected_source_type) {

    var cssClass = '.type-article #edit-form-article-content .fieldname-';
    var cssClasses = [];

    var classes = [
        'centerpage',
        'topicpage',
        'topicpage_filter',
        'elasticsearch_raw_query',
        'elasticsearch_raw_order',
    ];

    switch (selected_source_type.toLowerCase()) {
        case 'manuell':
            break;
        case 'centerpage':
            cssClasses.push('centerpage');
            break;
        case 'individuelle Abfrage':
            break;
        case 'tms-themenseite':
            cssClasses.push('topicpage');
            cssClasses.push('topicpage_filter');
            break;
        case 'es-query':
            cssClasses.push('elasticsearch_raw_query');
            cssClasses.push('elasticsearch_raw_order');
            break;
        default:
            break;
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

function eval_source_type(el) {
    var sel_val = el[0].selectedOptions[0].text;
    display_elements(sel_val);
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