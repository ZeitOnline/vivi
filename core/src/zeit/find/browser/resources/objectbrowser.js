zeit.cms.activate_objectbrowser = function(types) {
    // Activate the Search tab when there is one.
    var search_element = $('cp-search');
    if (search_element == null) {
        return false;
    }
    if (! isUndefinedOrNull(types)) {
        zeit.find._search.set_types(types);
    }
    zeit.find.tabs.activate('search_form');
    MochiKit.Visual.pulsate('cp-search', {
        duration:1,
        pulses:2
    });
    return true;
};
