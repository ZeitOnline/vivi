zeit.find = {};


zeit.find.init_search_results = function(view) {
    new zeit.find.SearchResultsDraggable(view);
    new zeit.find.Relateds(view);
    new zeit.find.ToggleFavorited(view);
}

zeit.find.BaseView = gocept.Class.extend({

    render: function() {
        var self = this;
        self.main_view.render();
    },

});

zeit.find.Search = zeit.find.BaseView.extend({

    construct: function(initial_query) {
        var self = this;
        self.initial_query = initial_query;
        var base_url = zeit.cms.get_application_url() + '/@@';
        // Initialize views
        self.main_view = new zeit.cms.JSONView(
            base_url + 'search_form', 'search_form');
        self.search_result = new zeit.cms.JSONView(
            base_url + 'search_result', 'search_result',
            MochiKit.Base.bind(self.search_form_parameters, self));
        self.result_filters = new zeit.cms.JSONView(
            base_url + 'result_filters', 'result_filters',
            MochiKit.Base.bind(self.search_form_parameters, self));
        // Connect handlers
        zeit.find.init_search_results(self.search_result);
        new zeit.find.ResultsFilters(self.search_result);
        new zeit.find.TimeFilters(self.result_filters);
        new zeit.find.AuthorFilters(self.result_filters);
        new zeit.find.TopicFilters(self.result_filters);
        new zeit.find.TypeFilters(self.result_filters);
        MochiKit.Signal.connect(
            self.main_view, 'load', self, self.init_search_form);
        MochiKit.Signal.connect(
            window, 'zeit.find.update-search', self, self.update_search_result);
    },

    init_search_form: function() {
        var self = this;
        MochiKit.Signal.connect('search_button', 'onclick', function(e) {
            self.update_search_result();
        });
        MochiKit.Signal.connect('search_form', 'onkeydown', function(e) {
            if (e.key().string == 'KEY_ENTER') {
                self.update_search_result();
                e.stop();
            };
        });
        MochiKit.Signal.connect('search_form', 'onchange', function(e) {
            self.update_search_result();
        });

        MochiKit.Signal.connect(
            'extended_search_button', 'onclick', function(e) {
            self.update_extended_search_info();
            MochiKit.DOM.toggleElementClass(
                'hidden', 'extended_search', 'extended_search_info');
        });
        MochiKit.Signal.connect(
            'result_filters_button', 'onclick', function(e) {
            if ($('result_filters_data')) {
                $('result_filters').innerHTML = '';
            } else {
                self.result_filters.render();
            }
        });
        if (!isUndefinedOrNull(self.initial_query)) {
            var form = $('zeit-find-search-form');
            var name;
            for (name in self.initial_query) {
                var element = form[name];
                if (isUndefinedOrNull(element)) {
                    continue
                }
                var value = self.initial_query[name]
                if (name == 'types:list') {
                    if (element.length != value.length) {
                        // Only act if not *everything* would be selected.
                        // Since selecting everyting is basically the same as
                        // selecting nothing
                        forEach(value, function(type) {
                            forEach(element, function(checkbox) {
                                if (checkbox.value == type) {
                                    checkbox.checked = true;
                                } else {
                                    checkbox.checked = false;
                                }
                            });
                        });
                    }
                } else {
                    element.value = value;
                }
            }
        }
        self.update_search_result();
    },

    update_search_result: function() {
        var self = this;
        log("updating search result");
        self.update_extended_search_info();
        self.search_result.render();
        if ($('result_filters_data')) {
            self.result_filters.render();
        }
    },

    update_extended_search_info: function() {
        var node = $('extended_search_info');
        node.innerHTML = '';
        forEach($('zeit-find-search-form').elements, function(element) {
            var value = null;
            var title = null;
            if (element.nodeName == 'SELECT') {
                var option = element.options[element.selectedIndex];
                title = option.text;
                value = option.value;
            } else if (element.nodeName == 'INPUT') {
                if (element.type == 'checkbox') {
                    if (element.checked) {
                        var label  = $$('label[for="' + element.id + '"]');
                        if (label.length != 1) {
                            return
                        }
                        value = element.value;
                        title = label[0].textContent;
                    }
                } else if (element.type == 'text' && element.name != 'text') {
                    value = element.value;
                    title = value;
                }
            }
            var default_value = element.getAttribute('default');
            if (title && value != default_value) {
                var class = 'info-' + element.name;
                node.appendChild(SPAN({'class': class}, title));
            }
        });
    },

    search_form_parameters: function() {
        var self = this;
        var qs = MochiKit.Base.queryString($('search_form'));
        return qs
    },

});

zeit.find.Favorites = zeit.find.BaseView.extend({
    // Put favorites into a $('favorites')

    construct: function() {
        var self = this;
        var base_url = zeit.cms.get_application_url() + '/@@';
        self.main_view = new zeit.cms.JSONView(
            base_url + 'favorites', 'favorites');
        zeit.find.init_search_results(self.main_view);
        MochiKit.Signal.connect(
            window, 'zeit.find.update-favorites',
            MochiKit.Base.bind(self.render, self));
    },
});

zeit.find.ForThisPage = zeit.find.BaseView.extend({

    construct: function() {
        var self = this;
        var base_url = zeit.cms.get_application_url() + '/@@';

        self.main_view = new zeit.cms.JSONView(
            context_url + '/@@for-this-page-search',
            'for-this-page')
        self.results = new zeit.cms.JSONView(
             base_url + 'search_result');
        zeit.find.init_search_results(self.results);
        MochiKit.Signal.connect(
             self.main_view, 'load', self, self.load);

    },

    load: function(element, data) {
        var self = this;
        var result_element = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'search_result', element);
        var search = MochiKit.Base.clone(data['search']);
        search['_path'] = null;
        self.results.render(result_element, null, search);
    }
});


zeit.find.init_full_search = function() {

    var search = new zeit.find.Search();

    zeit.find.tabs = new zeit.cms.Tabs('cp-search');
    zeit.find.tabs.add(new zeit.cms.ViewTab(
        'search_form', 'Suche', search));
    zeit.find.tabs.add(new zeit.cms.ViewTab(
        'favorites', 'Favoriten', new zeit.find.Favorites()));
    zeit.find.tabs.add(new zeit.cms.ViewTab(
        'for-this-page', 'Für diese Seite', new zeit.find.ForThisPage()));
}



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

    construct: function(view) {
        var self = this;
        arguments.callee.$.construct.call(self, view);
        self.expanded_search_result = new zeit.cms.JSONView(
            zeit.cms.get_application_url() + '/@@expanded_search_result')
    },

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
            var d = self.expanded_search_result.render(
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

    construct: function(view) {
        var self = this;
        arguments.callee.$.construct.call(self, view)
        var base_url = zeit.cms.get_application_url() + '/@@';
        self.favorited = new zeit.cms.JSONView(
            base_url + 'toggle_favorited');
    },

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
        var self = this;
        var d = self.favorited.render(toggle_favorited, favorite_url);
        d.addCallback(function(json) {
            MochiKit.DOM.setElementClass(
                toggle_favorited, json['favorited_css_class']);
            MochiKit.Signal.signal(window, 'zeit.find.update-favorites');
            return result;
        });

    },
});


zeit.find.TimeFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_time'));
        var from_field = $('zeit-find-search-form')['from'];
        var until_field = $('zeit-find-search-form')['until'];
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var start_date = lookup('start_date');
            var end_date = lookup('end_date');
            self.events.push(MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    from_field.value = start_date;
                    until_field.value = end_date;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
            }));
        });
    },

});


zeit.find.AuthorFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_author'));
        var author_field = $('zeit-find-search-form')['author'];
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var author = lookup('title');
            self.events.push( MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    author_field.value = author;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
            }));
        });
    },

});


zeit.find.TopicFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_topic'));
        var topic_field = $('zeit-find-search-form')['topic'];
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var topic = lookup('title');
            self.events.push(MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    topic_field.value = topic;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
            }));
        });
    },

});


zeit.find.TypeFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'a', 'filter_link', $('filter_type'));
        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);
            var type = lookup('type');
            self.events.push(MochiKit.Signal.connect(
                entry, 'onclick', function(e) {
                    forEach($('zeit-find-search-form')['types:list'],
                            function(checkbox) {
                        if (checkbox.value == type) {
                            checkbox.checked = true;
                        } else {
                            checkbox.checked = false;
                        }
                    });
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
            }));
        });
    },

});

zeit.find.ResultsFilters = zeit.find.Component.extend({

    connect: function(element, data) {
        var self = this;
        var form = $('zeit-find-search-form')
        var from_field = form['from'];
        var until_field = form['until'];
        var volume_year_field = form['volume_year'];
        var topic_field = form['topic'];
        var author_field = form['author'];

        var results = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'search_entry', element);

        forEach(results, function(entry) {
            var lookup = jsontemplate.get_node_lookup(data, entry);

            var start_date = lookup('start_date');
            var end_date = lookup('end_date');
            var date_filter = MochiKit.Selector.findChildElements(
                entry, ['.date_filter'])[0];
            self.events.push(MochiKit.Signal.connect(
                date_filter, 'onclick', function(e) {
                    from_field.value = start_date;
                    until_field.value = end_date;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));
           
            var volume_year = lookup('volume_year');
            var volume_year_filter = MochiKit.Selector.findChildElements(
                entry, ['.volume_year_filter'])[0];
            self.events.push(MochiKit.Signal.connect(
                volume_year_filter, 'onclick', function(e) {
                    volume_year_field.value = volume_year;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));

            var topic = lookup('topic');
            var topic_filter = MochiKit.Selector.findChildElements(
                entry, ['.topic_filter'])[0];
            self.events.push(MochiKit.Signal.connect(
                topic_filter, 'onclick', function(e) {
                    topic_field.value = topic;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));
            
            var author_filters = MochiKit.Selector.findChildElements(
                entry, ['.author_filter']);
            forEach(author_filters, function(author_filter) {
                var author_lookup = jsontemplate.get_node_lookup(
                    data, author_filter);
                var author = author_lookup('@');
                self.events.push(MochiKit.Signal.connect(
                    author_filter, 'onclick', function(e) {
                        author_field.value = author;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));
            });
            
        });
    }
});


zeit.find.Selector = gocept.Class.extend({
    
    construct: function(lightbox_form, search) {
        var self = this;
        self.lightbox_form = lightbox_form;
        self.search = search;
        var ident = MochiKit.Signal.connect(
            self.search.main_view, 'load', function() {
            MochiKit.Signal.disconnect(ident);
            self.event = MochiKit.Signal.connect(
                'search_result', 'onclick', self, self.select_object);
        });
    },

    select_object: function(event) {
        var self = this;
        var target = event.target();
        if (target.nodeName == 'A') {
            return

        }
        var unique_id = null;
        var selected_element = null;
        while (isNull(unique_id) ||
               MochiKit.DOM.hasElementClass(target, 'search_entry')) {
            var unique_id = MochiKit.DOM.getFirstElementByTagAndClassName(
                null, 'uniqueId', target);
            selected_element = target;
            target = target.parentNode;
        }
        if (isNull(unique_id)) {
            return
        }
        event.stop();
        unique_id = unique_id.textContent;
        MochiKit.Signal.signal(
            self.lightbox_form,
            'zeit.cms.ObjectReferenceWidget.selected',
            unique_id, selected_element);
    },
});
