function getFieldClassNames() {
    return {
        'automatic_type': 'field fieldname-automatic_type fieldtype-text',
        'first_reference': 'field fieldname-first_reference fieldtype-text',
        'second_reference': 'field fieldname-second_reference fieldtype-text',
        'third_reference': 'field fieldname-third_reference fieldtype-text',
        'referenced_cp': 'field fieldname-referenced_cp fieldtype-text',
        'referenced_topicpage': 'field fieldname-referenced_topicpage fieldtype-text',
        'topicpage_filter': 'field fieldname-topicpage_filter fieldtype-text',
        'elasticsearch_raw_query': 'field fieldname-elasticsearch_raw_query fieldtype-text',
        'elasticsearch_raw_order': 'field fieldname-elasticsearch_raw_order fieldtype-text',
        'preconfigured_query': 'field fieldname-preconfigured_query fieldtype-text',
        'topicpage_order': 'field fieldname-topicpage_order required fieldtype-text',
    };
}

function getAllTopicboxIds() {
    var topicbox_ids = [];

    document.querySelectorAll('.type-topicbox').forEach((topicbox) => {
        topicbox_ids.push(topicbox.id);
    });

    return topicbox_ids;
}

function getAutomaticTypeTextByTopicboxId(topicboxId) {
    var automaticTypeElement = document.getElementById(`topicbox.${topicboxId}.automatic_type`);

    if (automaticTypeElement !== null) {
        return automaticTypeElement.selectedOptions[0].text;
    }
    return null;
}

function displayElements(event) {
    // 'fragment-ready' is called, if the document is reloading
    // 'changed' is called, if a automatic_type value is changed
    var topicboxIds = getAllTopicboxIds();
    if (event.type === 'fragment-ready') {
        topicboxIds.forEach((topicboxId) => {
            hideShowElementsByAutomaticTypeValue(topicboxId);
        });
    } else if (event.type === 'change') {
        var topicboxId = (event.target.id.replace('topicbox.', '').replace('.automatic_type', ''));
        hideShowElementsByAutomaticTypeValue(topicboxId);
    } else {
        console.log(`unhandled event: ${event.type}`);
    }
}

function getTopicboxFieldSetById(topicboxId) {
    return document.getElementById(`form-topicbox.${topicboxId}`);
}

function hideShowElementsByAutomaticTypeValue(topicboxId) {
    var topicboxFieldSet = getTopicboxFieldSetById(topicboxId);
    var fieldClassNames = getFieldClassNames();
    var currentAutomaticTypeValue = getAutomaticTypeTextByTopicboxId(topicboxId);

    if (currentAutomaticTypeValue === null) {
        return;
    }

    // Hide all except automatic_type
    Object.keys(fieldClassNames).filter((element) => {
        return element.indexOf('automatic_type') == -1;
    }).forEach((element) => {
        hideElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
    });

    var automaticFields = [];
    switch(currentAutomaticTypeValue.toLowerCase()) {
        case 'klassisch':
            automaticFields = [
                'first_reference',
                'second_reference',
                'third_reference'];
            break;
        case 'centerpage':
            automaticFields = [
                'referenced_cp'
            ];
            break;
        case 'themenseite':
            automaticFields = [
                'referenced_topicpage',
                'topicpage_filter',
                'topicpage_order'
            ];
            break;
        case 'es-query':
            automaticFields = [
                'elasticsearch_raw_query',
                'elasticsearch_raw_order'
            ];
            break;
        case 'related-api':
            automaticFields = [
                'topicpage_filter'
            ];
            break;
        case 'filter':
            automaticFields = [
                'preconfigured_query'
            ];
            break;
        default:
            break;
    }

    Object.keys(fieldClassNames).filter((element) => {
        return automaticFields.includes(element);
    }).forEach((element) => {
        showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
    });
}

function hideElementByTopicboxFieldSet(fieldset, className) {
    fieldset.querySelectorAll(`[class="${className}"]`)[0].style.display = 'none';
}

function showElementByTopicboxFieldSet(fieldset, className) {
    fieldset.querySelectorAll(`[class="${className}"]`)[0].style.display = 'block';
}

(function ($) {
    $(document).bind('fragment-ready', function(event) {
        getAllTopicboxIds().forEach(() => {
            displayElements(event);
        });
    });

    $(document).bind('change', function(event) {
        if (event.target && event.target.id.indexOf('automatic_type') > -1) {
            displayElements(event);
        }
    });
 }(jQuery));
