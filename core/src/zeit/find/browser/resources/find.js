zeit.find = {};

(function() {

    var init_search_form = function() {
        MochiKit.Signal.connect('search_button', 'onclick', function(e) {
            zeit.find.search_result.render();
        });
        MochiKit.Signal.connect('cp-search', 'onkeydown', function(e) {
            if (e.key().string == 'KEY_ENTER') {
                zeit.find.search_result.render();
                e.stop();
            };
        });

        MochiKit.Signal.connect(
            'extended_search_button', 'onclick', function(e) {
            if (MochiKit.Style.getStyle($('extended_search'), 'display')
                == 'none') {
                MochiKit.Style.showElement($('extended_search'));
            } else {
                MochiKit.Style.hideElement($('extended_search'));
            }
        });
        MochiKit.Signal.connect(
            'result_filters_button', 'onclick', function(e) {
            if ($('filter_time')) {
                $('result_filters').innerHTML = '';
            } else {
                zeit.find.result_filters.render();
            }
        });
    };

    var for_this_page_loader = function(element, data) {
        var result_element = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'search_result', element);
        var search = MochiKit.Base.clone(data['search']);
        search['_path'] = null;
        zeit.find.for_this_page_results.render(result_element, null, search);
    }


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

        //zeit.find.for_this_page = new zeit.cms.JSONView(
        //    context_url + '/@@for-this-page-search',
        //    'for-this-page')
        //zeit.find.for_this_page_results = new zeit.cms.JSONView(
        //     base_url + 'search_result');

        MochiKit.Signal.connect(zeit.find.search_form, 'load', init_search_form);

        var search_results = function(view) {
            new zeit.find.SearchResultsDraggable(view);
            new zeit.find.Relateds(view);
            new zeit.find.ToggleFavorited(view);
        }

        search_results(zeit.find.search_result);
        search_results(zeit.find.favorites);
        //search_results(zeit.find.for_this_page_results);

        new zeit.find.TimeFilters(zeit.find.result_filters);
        new zeit.find.AuthorFilters(zeit.find.result_filters);
        new zeit.find.TopicFilters(zeit.find.result_filters);
        new zeit.find.TypeFilters(zeit.find.result_filters);

        //MochiKit.Signal.connect(
        //     zeit.find.for_this_page, 'load', for_this_page_loader);

        zeit.find.search_form.render();
        zeit.find.tabs = new zeit.cms.Tabs('cp-search');
        zeit.find.tabs.add(new zeit.cms.ViewTab(
            'search_form', 'Suche', zeit.find.search_result));
        zeit.find.tabs.add(new zeit.cms.ViewTab(
            'favorites', 'Favoriten', zeit.find.favorites));
        //zeit.find.tabs.add(new zeit.cms.ViewTab(
        //    'for-this-page', 'Für diese Seite', zeit.find.for_this_page));
    };

    var search_form_parameters = function() {
        return MochiKit.Base.queryString($('search_form'));
    };

    MochiKit.Signal.connect(window, 'onload', init);

})();


zeit.find.Component = gocept.Class.extend({

    construct: function(view) {
        var self = this;
        self.view = view;
        MochiKit.Signal.connect(view, 'load', self, self.on_load);
        self.events = []
        self.draggables = [];
    },

    on_load: function(element, data) {
        var self = this;
        self.disconnect();
        self.connect(element, data);
    },

    disconnect: function() {
        var self = this;
        while(self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop())
        }
        while(self.draggables.length) {
            self.draggables.pop().destroy();
        }
    },

});

zeit.find.Relateds = zeit.find.Component.extend({
    // Handles relateds of *one* search result entry.

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', element);
        forEach(results, function(entry) {
            var related_url = jsontemplate.get_node_lookup(data, entry)(
                'related_url');
            var related_links = MochiKit.Selector.findChildElements(
                entry, ['.related_links'])[0];
            var related_info = MochiKit.Selector.findChildElements(
                entry, ['.related_info'])[0];
            self.events.push(
                MochiKit.Signal.connect(related_links, 'onclick', function() {
                    self.toggle(related_links, related_info, related_url);
            }));
        });
    },

    connect_draggables: function(related_info) {
        var self = this;
        var related_entries = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'related_entry', related_info);
        forEach(related_entries, function(related) {
            self.draggables.push(
                zeit.cms.createDraggableContentObject(related));
        });
    },

    toggle: function(related_links, related_info, related_url) {
        var self = this;
        if (MochiKit.DOM.hasElementClass(related_links, 'expanded')) {
            MochiKit.DOM.removeElementClass(
                related_links, 'expanded');
            related_info.innerHTML = '';
        } else {
            MochiKit.DOM.addElementClass(related_links, 'expanded');
            var d = zeit.find.expanded_search_result.render(
                related_info, related_url);
            d.addCallback(function(result) {
                self.connect_draggables(related_info)
                return result;
            });
        }
    },
});


zeit.find.SearchResultsDraggable = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', element);
        forEach(results, function(result) {
            self.draggables.push(zeit.cms.createDraggableContentObject(result));
        });
    },


});

zeit.find.ToggleFavorited = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', element);
        forEach(results, function(entry) {
            var favorite_url = jsontemplate.get_node_lookup(data, entry)(
                'favorite_url');
            var toggle_favorited = MochiKit.Selector.findChildElements(
                entry, ['.toggle_favorited'])[0];
            self.events.push(MochiKit.Signal.connect(
                toggle_favorited, 'onclick', function(e) {
                    self.toggle(toggle_favorited, favorite_url);
            }));
        });
    },


    toggle: function(toggle_favorited, favorite_url) {
        var d = zeit.find.favorited.render(toggle_favorited, favorite_url);
        d.addCallback(function(result) {
            zeit.find.favorites.render();
            return result;
        });

    },
});


zeit.find.TimeFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_time'));
        var from_field = $('from');
        var until_field = $('until');
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var start_date = lookup('start_date');
            var end_date = lookup('end_date');
            self.events.push(MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    from_field.value = start_date;
                    until_field.value = end_date;
                    zeit.find.search_result.render();
            }));
        });
    },

});


zeit.find.AuthorFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_author'));
        var author_field = $('author');
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var author = lookup('title');
            self.events.push( MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    author_field.value = author;
                    zeit.find.search_result.render();
            }));
        });
    },

});


zeit.find.TopicFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_topic'));
        var topic_field = $('topic');
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var topic = lookup('title');
            self.events.push(MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    topic_field.value = topic;
                    zeit.find.search_result.render();
            }));
        });
    },

});


zeit.find.TypeFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
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
            self.events.push(MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    for (var i = 0; i < checkbox_ids.length; i++) {
                        checkbox_fields[checkbox_ids[i]].checked = false;
                    }
                    checkbox_fields[checkbox_id].checked = true;
                    zeit.find.search_result.render();
            }));
        });
    },

});

