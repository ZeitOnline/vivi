zeit.cms.activate_objectbrowser = function() {
    // Activate the Search tab when there is one.
    var search_element = $('cp-search')
    if (search_element) {
        zeit.find.tabs.activate('search_form');
        MochiKit.Visual.pulsate('cp-search', {
            duration:1,
            pulses:2,
        })
        return true;
    }
    return false;
}
