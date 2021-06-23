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

    switch(currentAutomaticTypeValue.toLowerCase()) {
        case 'klassisch':
            Object.keys(fieldClassNames).filter((element) => {
                return [
                    'first_reference',
                    'second_reference',
                    'third_reference'].includes(element);
            }).forEach((element) => {
                showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
            });
            break;
        case 'centerpage':
            Object.keys(fieldClassNames).filter((element) => {
                return ['referenced_cp'].includes(element);
            }).forEach((element) => {
                showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
            });
            break;
        case 'themenseite':
            Object.keys(fieldClassNames).filter((element) => {
                return [
                    'referenced_topicpage',
                    'topicpage_filter'].includes(element);
            }).forEach((element) => {
                showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
            });
            break;
        case 'es-query':
            Object.keys(fieldClassNames).filter((element) => {
                return [
                    'elasticsearch_raw_query',
                    'elasticsearch_raw_order'].includes(element);
            }).forEach((element) => {
                showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
            });
            break;
        case 'related-api':
            Object.keys(fieldClassNames).filter((element) => {
                return ['topicpage_filter'].includes(element);
            }).forEach((element) => {
                showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
            });
            break;
        case 'filter':
            Object.keys(fieldClassNames).filter((element) => {
                return ['preconfigured_query'].includes(element);
            }).forEach((element) => {
                showElementByTopicboxFieldSet(topicboxFieldSet, fieldClassNames[element]);
            });
            break;
        default:
            break;
    }
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
