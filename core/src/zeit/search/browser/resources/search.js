zeit.search = {}

zeit.search.Search = Class.extend({

    construct: function() {
        this.form = $('search-form');
        connect('search-extended-show',  'onclick', this, 'show');
        connect('search-extended-hide',  'onclick', this, 'hide');
    },

    toggle: function() {
        var url = application_url + "/@@toggle-extended-search";
        MochiKit.Async.doSimpleXMLHttpRequest(url);
    },

    show: function() {
        this.toggle();
        MochiKit.DOM.removeElementClass(this.form, 'hide-extended');
        MochiKit.DOM.addElementClass(this.form, 'show-extended');
        MochiKit.Signal.signal('sidebar', 'panel-content-changed');
    },
    
    hide: function() {
        this.toggle();
        this.fill_extended_search_indicator();
        MochiKit.DOM.removeElementClass(this.form, 'show-extended');
        MochiKit.DOM.addElementClass(this.form, 'hide-extended');
        MochiKit.Signal.signal('sidebar', 'panel-content-changed');
    },
    
    fill_extended_search_indicator: function() {
        var othis = this;
        result = []
        forEach(this.form.elements, function(element) {
            if (element.id == 'search.sort') {
                // Ignore sorting
                return
            }
            var value = '';
            if (element.nodeName == 'INPUT') {
                value = element.value;
            } else if (element.nodeName == 'SELECT') {
                value = element.options[element.selectedIndex].text;
            }

            if (!value) {
                return 
            }
            var label = $$('label[for="' + element.id + '"]');
            if (isEmpty(label)) {
                return
            }
            result.push('+ ' + label[0].textContent + ': ' + value);
        });
        var contents = '';
        if (result.length > 0) {
            contents = result.join('\n');
        }
        var indicator = $('search-extended-indicator');
        indicator.innerHTML = ''
        indicator.appendChild(SPAN({}, contents));
    },

});


connect(window, 'onload', function(event) {
    new zeit.search.Search()
});
