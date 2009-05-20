zeit.find = {};

(function() {

    var init_search_form = function() {
        MochiKit.Signal.connect('search_button', 'onclick', function(e) {
            zeit.find.search_result.render();
        });
        MochiKit.Signal.connect('fulltext', 'onkeydown', function(e) {
            if (e.key()['string'] == 'KEY_ENTER') {
                zeit.find.search_result.render();
                e.stop();
            };
        });

        MochiKit.Signal.connect('extended_search_button', 'onclick', function(e) {
            if ($('extended_search')) {
                $('extended_search_form').innerHTML = '';
            } else {
                zeit.find.extended_search_form.render();
            }
        });
        MochiKit.Signal.connect('result_filters_button', 'onclick', function(e) {
            if ($('filter_Zeit')) {
                $('result_filters').innerHTML = '';
            } else {
                zeit.find.result_filters.render();
            }
        });
    };

    var draggables = [];

    var connect_draggables = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('cp-search'));
        forEach(results, function(result) {
            draggables.push(zeit.cms.createDraggableContentObject(result));
        });
    }

    var connect_related = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('cp-search'));
        forEach(results, function(entry) {
            var related_url = MochiKit.DOM.scrapeText(
                MochiKit.Selector.findChildElements(
                    entry, ['.related_url'])[0]);
            var related_links = MochiKit.Selector.findChildElements(
                entry, ['.related_links'])[0];
            var related_info = MochiKit.Selector.findChildElements(
                entry, ['.related_info'])[0];
            MochiKit.Signal.connect(related_links, 'onclick', function(e) {
                if (MochiKit.DOM.hasElementClass(related_links, 'expanded')) {
                    MochiKit.DOM.removeElementClass(related_links, 'expanded');
                    related_info.innerHTML = '';
                } else {
                    MochiKit.DOM.addElementClass(related_links, 'expanded');
                    zeit.find.expanded_search_result.render(
                        related_info, related_url);
                }
            });
        });
    }

    var connect_toggle_favorited = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('cp-search'));
        forEach(results, function(entry) {
            var favorite_url = MochiKit.DOM.scrapeText(
                MochiKit.Selector.findChildElements(
                    entry, ['.favorite_url'])[0]);
            var toggle_favorited = MochiKit.Selector.findChildElements(
                entry, ['.toggle_favorited'])[0];
            MochiKit.Signal.connect(toggle_favorited, 'onclick', function(e) {
                zeit.find.favorited.render(
                    toggle_favorited, favorite_url);
            });
        });
    }

    var disconnect_draggables = function() {
        while(draggables.length > 0) {
            draggables.pop().destroy();
        }
    }

    var init = function() {

        var base_url = application_url + '/@@';
        zeit.find.search_form = new zeit.cms.JSONView(
            base_url + 'search_form', 'search_form');
        zeit.find.search_result = new zeit.cms.JSONView(
            base_url + 'search_result', 'search_result',
            search_form_parameters);
        zeit.find.extended_search_form = new zeit.cms.JSONView(
            base_url + 'extended_search_form', 'extended_search_form');
        zeit.find.result_filters = new zeit.cms.JSONView(
            base_url + 'result_filters', 'result_filters',
            search_form_parameters);
        zeit.find.expanded_search_result = new zeit.cms.JSONView(
            base_url + 'expanded_search_result')
        zeit.find.favorited = new zeit.cms.JSONView(
            base_url + 'toggle_favorited')
        zeit.find.favorites = new zeit.cms.JSONView(
            base_url + 'favorites', 'favorites');

        MochiKit.Signal.connect(zeit.find.search_form, 'load', init_search_form);

        MochiKit.Signal.connect(zeit.find.search_result, 'load',
                                connect_related);
        
        MochiKit.Signal.connect(zeit.find.search_result, 'load',
                                connect_toggle_favorited);

        MochiKit.Signal.connect(zeit.find.search_result, 'load',
                                connect_draggables);
        MochiKit.Signal.connect(zeit.find.search_result, 'before-load',
                                disconnect_draggables);
      
        MochiKit.Signal.connect(zeit.find.favorites, 'load',
                                connect_related);
        MochiKit.Signal.connect(zeit.find.favorites, 'load',
                                connect_toggle_favorited);

        MochiKit.Signal.connect(zeit.find.favorites, 'load',
                                connect_draggables);
        MochiKit.Signal.connect(zeit.find.favorites, 'before-load',
                                disconnect_draggables);

        zeit.find.search_form.render();
        zeit.find.tabs = new zeit.cms.Tabs('cp-search');
        zeit.find.tabs.add(new zeit.cms.ViewTab(
            'search_form', 'Suche', zeit.find.search_result));
        zeit.find.tabs.add(new zeit.cms.ViewTab(
            'favorites', 'Favoriten', zeit.find.favorites));
        zeit.find.tabs.add(new zeit.cms.Tab(
            'for-this-page', 'Für diese Seite'));
    };

    var search_form_parameters = function() {
        return MochiKit.Base.queryString($('search_form'));
    };

    MochiKit.Signal.connect(window, 'onload', init);

})();
