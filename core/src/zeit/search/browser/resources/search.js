function toggle() {
    var url = "/@@toggle-extended-search"
    doSimpleXMLHttpRequest(url);
}

connect(window, 'onload', function(event) {
    var switch_element = 'search-form'
    connect('search-extended-show',  'onclick', function() {
        toggle();
        removeElementClass(switch_element, 'hide-extended');
        addElementClass(switch_element, 'show-extended');
    });
    connect('search-extended-hide',  'onclick', function() {
        toggle();
        removeElementClass(switch_element, 'show-extended');
        addElementClass(switch_element, 'hide-extended');
    });
});
