function getAllTopicboxIds() {
    var topicbox_ids = [];

    document.querySelectorAll('.type-topicbox').forEach((topicbox) => {
        topicbox_ids.push(topicbox.id);
    });

    return topicbox_ids;
}

function getAutomaticTypeByTopicboxId(topicboxId) {
    var automaticTypeElement = document.getElementById(`topicbox.${topicboxId}.automatic_type`);

    if (automaticTypeElement !== null) {
        return automaticTypeElement.selectedOptions[0].value;
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
    var currentAutomaticTypeValue = getAutomaticTypeByTopicboxId(topicboxId);
    if (currentAutomaticTypeValue === null) {
        return;
    }

    var allAutomaticFields = [
        'first_reference', 'second_reference', 'third_reference',
        'referenced_cp',
        'referenced_topicpage', 'topicpage_filter', 'topicpage_order',
        'elasticsearch_raw_query', 'elasticsearch_raw_order',
        'preconfigured_query'
    ];

    // Hide all except automatic_type
    allAutomaticFields.forEach((element) => {
        hideElementByTopicboxFieldSet(topicboxFieldSet, `fieldname-${element}`);
    });

    var automaticFields = [];
    switch(currentAutomaticTypeValue.toLowerCase()) {
        case 'manual':
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
        case 'topicpage':
            automaticFields = [
                'referenced_topicpage',
                'topicpage_filter',
                'topicpage_order'
            ];
            break;
        case 'elasticsearch-query':
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
        case 'preconfigured-query':
            automaticFields = [
                'preconfigured_query'
            ];
            break;
        default:
            break;
    }

    allAutomaticFields.filter((element) => {
        return automaticFields.includes(element);
    }).forEach((element) => {
        showElementByTopicboxFieldSet(topicboxFieldSet, `fieldname-${element}`);
    });
}

function hideElementByTopicboxFieldSet(fieldset, className) {
    fieldset.querySelectorAll(`.${className}`)[0].style.display = 'none';
}

function showElementByTopicboxFieldSet(fieldset, className) {
    fieldset.querySelectorAll(`.${className}`)[0].style.display = 'block';
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
