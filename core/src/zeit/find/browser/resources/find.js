zeit.find = {};

(function() {

    var init_search_form = function() {
        MochiKit.Signal.connect('search_button', 'onclick', function(e) {
            search_result.render();
        });
        MochiKit.Signal.connect('extended_search_button', 'onclick', function(e) {
            if ($('extended_search')) {
                $('extended_search_form').innerHTML = '';
            } else {
                extended_search_form.render();
            }
        });
        MochiKit.Signal.connect('result_filters_button', 'onclick', function(e) {
            if ($('filter_Zeit')) {
                $('result_filters').innerHTML = '';
            } else {
                result_filters.render();
            }
        });
    };

    var draggables = [];

    var connect_draggables = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('cp-forms'));
        forEach(results, function(result) {
            draggables.push(zeit.cms.createDraggableContentObject(result));
        });
    }

    var connect_related = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('cp-forms'));
        forEach(results, function(entry) {
            var related_url = MochiKit.DOM.scrapeText(
                MochiKit.Selector.findChildElements(
                    entry, ['.related_url'])[0]);
            var related_links = MochiKit.Selector.findChildElements(
                entry, ['.related_links'])[0];
            var related_info = MochiKit.Selector.findChildElements(
                entry, ['.related_info'])[0];
            MochiKit.Signal.connect(related_links, 'onclick', function(e) {
                if (MochiKit.Selector.findChildElements(related_info,
                                                        ['.related_entry']).length > 0) {
                    MochiKit.DOM.removeElementClass(related_links, 'expanded');
                    related_info.innerHTML = '';
                } else {
                    MochiKit.DOM.addElementClass(related_links, 'expanded');
                    expanded_search_result.render(related_info, related_url);
                }
            });
        });
    }

    var connect_toggle_favorited = function() {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', $('cp-forms'));
        forEach(results, function(entry) {
            var favorite_url = MochiKit.DOM.scrapeText(
                MochiKit.Selector.findChildElements(
                    entry, ['.favorite_url'])[0]);
            var toggle_favorited = MochiKit.Selector.findChildElements(
                entry, ['.toggle_favorited'])[0];
            MochiKit.Signal.connect(toggle_favorited, 'onclick', function(e) {
                favorited.render(toggle_favorited, favorite_url);
            });
        });
    }

    var disconnect_draggables = function() {
        while(draggables.length > 0) {
            draggables.pop().destroy();
        }
    }

    var init = function() {
        search_form.render();
        zeit.find.tabs = new zeit.cms.Tabs('cp-forms');
        zeit.find.tabs.add(new zeit.cms.ViewTab('search_form', 'Suche', search_result));
        zeit.find.tabs.add(new zeit.cms.ViewTab('favorites', 'Favoriten', favorites));
        zeit.find.tabs.add(new zeit.cms.Tab('for-this-page', 'Für diese Seite'));
    };

    search_form = new zeit.cms.JSONView(
        'search_form', 'search_form');
    search_result = new zeit.cms.JSONView(
        'search_result', 'search_result',
        function() {
            return MochiKit.Base.queryString($('search_form'));
        });
    extended_search_form = new zeit.cms.JSONView(
        'extended_search_form', 'extended_search_form');
    result_filters = new zeit.cms.JSONView(
        'result_filters', 'result_filters')
    expanded_search_result = new zeit.cms.JSONView(
        'expanded_search_result')
    favorited = new zeit.cms.JSONView(
        'toggle_favorited')
    favorites = new zeit.cms.JSONView(
        'favorites', 'favorites');

    MochiKit.Signal.connect(window, 'onload', init);
    MochiKit.Signal.connect(search_form, 'load', init_search_form);

    MochiKit.Signal.connect(search_result, 'before-load',
                            disconnect_draggables);
    MochiKit.Signal.connect(search_result, 'load',
                            connect_related);
    MochiKit.Signal.connect(search_result, 'load',
                            connect_toggle_favorited);
    MochiKit.Signal.connect(search_result, 'load',
                            connect_draggables);

    MochiKit.Signal.connect(favorites, 'before-load',
                            disconnect_draggables);
    MochiKit.Signal.connect(favorites, 'load',
                            connect_related);
    MochiKit.Signal.connect(favorites, 'load',
                            connect_toggle_favorited);
    MochiKit.Signal.connect(favorites, 'load',
                            connect_draggables);

    MochiKit.Signal.connect(favorited, 'load',
                            function() {
                                favorites.render();
                            });

})();
