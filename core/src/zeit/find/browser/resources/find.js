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
            if (MochiKit.Style.getStyle($('extended_search'), 'display') == 'none') {
                MochiKit.Style.showElement($('extended_search'));
            } else {
                MochiKit.Style.hideElement($('extended_search'));
            }
        });
        MochiKit.Signal.connect('result_filters_button', 'onclick', function(e) {
            if ($('filter_time')) {
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

    var disconnect_draggables = function() {
        while(draggables.length > 0) {
            draggables.pop().destroy();
        }
    }

    var connect_related = function(element, data) {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', element);
        forEach(results, function(entry) {
            var related_url = jsontemplate.get_node_lookup(data, entry)('related_url');
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

    var connect_toggle_favorited = function(element, data) {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', element);
        forEach(results, function(entry) {
            var favorite_url = jsontemplate.get_node_lookup(data, entry)('favorite_url');
            var toggle_favorited = MochiKit.Selector.findChildElements(
                entry, ['.toggle_favorited'])[0];
            MochiKit.Signal.connect(toggle_favorited, 'onclick', function(e) {
                zeit.find.favorited.render(
                    toggle_favorited, favorite_url);
            });
        });
    }

    var connect_time_filters = function(element, data) {;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_time'));
        var from_field = $('from');
        var until_field = $('until');
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var start_date = lookup('start_date');
            var end_date = lookup('end_date');
            MochiKit.Signal.connect(entry, 'onclick', function(e) {
                from_field.value = start_date;
                until_field.value = end_date;
                zeit.find.search_result.render();
            });
        });
    };


    var connect_author_filters = function(element, data) {;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_author'));
        var author_field = $('author');
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var author = lookup('title');
            MochiKit.Signal.connect(entry, 'onclick', function(e) {
                author_field.value = author;
                zeit.find.search_result.render();
            });
        });
    };

    var connect_topic_filters = function(element, data) {;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_topic'));
        var topic_field = $('topic');
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var topic = lookup('title');
            MochiKit.Signal.connect(entry, 'onclick', function(e) {
                topic_field.value = topic;
                zeit.find.search_result.render();
            });
        });
    };

    var connect_type_filters = function(element, data) {
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_type'));
        var checkbox_ids = ['article', 'gallery', 'video', 'teaser', 'centerpage'];
        var checkbox_fields = {};
        for (var i = 0; i < checkbox_ids.length; i++) {
            var checkbox_id = checkbox_ids[i];
            checkbox_fields[checkbox_id] = $(checkbox_id);
        }
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var checkbox_id = lookup('title');
            MochiKit.Signal.connect(entry, 'onclick', function(e) {
                for (var i = 0; i < checkbox_ids.length; i++) {
                    checkbox_fields[checkbox_ids[i]].checked = false;
                }
                checkbox_fields[checkbox_id].checked = true;
                zeit.find.search_result.render();
            });
        });
    };

    var init = function() {

        var base_url = application_url + '/@@';
        zeit.find.search_form = new zeit.cms.JSONView(
            base_url + 'search_form', 'search_form');
        zeit.find.search_result = new zeit.cms.JSONView(
            base_url + 'search_result', 'search_result',
            search_form_parameters);
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
        
        MochiKit.Signal.connect(zeit.find.result_filters, 'load',
                                connect_time_filters);
        MochiKit.Signal.connect(zeit.find.result_filters, 'load',
                                connect_author_filters);
        MochiKit.Signal.connect(zeit.find.result_filters, 'load',
                                connect_topic_filters);
        MochiKit.Signal.connect(zeit.find.result_filters, 'load',
                                connect_type_filters);

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
