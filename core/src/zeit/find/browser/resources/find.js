zeit.cms.declare_namespace('zeit.find');


zeit.find.init_search_results = function(view) {
    new zeit.find.SearchResultsDraggable(view);
    new zeit.find.ToggleFavorited(view);
};


zeit.find.Search = gocept.Class.extend({

    construct: function(submit_on_pageload) {
        var self = this;
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

        self.submit_on_pageload = submit_on_pageload;

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

    render: function() {
        var self = this;
        self.main_view.render();
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

        MochiKit.Signal.connect('reset_search_button', 'onclick', function(e) {
            self.reset_search_form();
        });

        MochiKit.Signal.connect(
            'type_search_button', 'onclick', function() {
                self.toggle_type_search(true);
        });
        MochiKit.Signal.connect(
            'extended_search_button', 'onclick', function() {
                self.toggle_extended_search(true);
        });
        MochiKit.Signal.connect(
            'result_filters_button', 'onclick', function() {
            self.toggle_result_filters(true);
        });

        var d = MochiKit.Async.loadJSONDoc(
            zeit.cms.get_application_url() + '/@@zeit.find.last-query');
        d.addCallbacks(
            function(json) {
                self.populate_query(json);
                return json
            },
            function(error) {
                zeit.cms.log_error(error);
                return error;
        });
        d.addCallback(function(json) {
            var field = $('zeit-find-search-form')['type_search_expanded'];
            if (field.value) {
                self.toggle_type_search(false);
            }
            var field = $('zeit-find-search-form')['extended_search_expanded'];
            if (field.value) {
                self.toggle_extended_search(false);
            }
            var field = $('zeit-find-search-form')['result_filters_expanded'];
            if (field.value) {
                self.toggle_result_filters(false);
            }
            return json;
        });
    },

    clear_search_params: function() {
        var self = this;
        forEach($('zeit-find-search-form').elements, function(element) {
            if (element.nodeName == 'SELECT') {
                var default_value = element.getAttribute('default');
                var index = 0;
                if (default_value) {
                    var default_option = jQuery(
                        'option[value="' + default_value + '"]', element);
                    index = default_option.index();
                }
                element.selectedIndex = index;
            } else if (element.nodeName == 'INPUT') {
                if (element.type == 'checkbox') {
                    element.checked = false;
                } else if (element.type == 'text') {
                    element.value = '';
                }
            }
        });
    },

    reset_search_form: function() {
        var self = this;
        self.clear_search_params();

        // If toggleElementClass had a "force state on/off" parameter, we could
        // reuse the self.toggle_* functions here, sigh.
        MochiKit.DOM.addElementClass('type_search', 'hidden');
        MochiKit.DOM.addElementClass('type_search_info', 'hidden');
        MochiKit.DOM.removeElementClass('type_search_button', 'unfolded');

        MochiKit.DOM.addElementClass('extended_search', 'hidden');
        MochiKit.DOM.addElementClass('extended_search_info', 'hidden');
        MochiKit.DOM.removeElementClass('extended_search_button', 'unfolded');

        $('zeit-find-search-form')['type_search_expanded'].value = '';
        $('zeit-find-search-form')['extended_search_expanded'].value = '';

        self.update_search_result();
    },

    set_types: function(types) {
        var self = this;
        self.clear_search_params();
        forEach(types, function(type) {
            jQuery('input[type="checkbox"][value="' + type + '"]',
                   $('zeit-find-search-form')).attr('checked', 'checked');
        });
        self.update_search_result();
    },

    populate_query: function(query) {
        var self = this;
        var form = $('zeit-find-search-form');
        var name;
        for (name in query) {
            var element = form[name];
            if (isUndefinedOrNull(element)) {
                continue
            }
            var value = query[name]
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
        if (self.submit_on_pageload) {
            self.update_search_result();
        }
    },

    update_search_result: function() {
        var self = this;
        log("updating search result");
        self.update_extended_search_info(
            $('type_search'), $('type_search_info'));
        self.update_extended_search_info(
            $('extended_search'), $('extended_search_info'));
        self.search_result.render();
        if ($('result_filters_data')) {
            self.result_filters.render();
        }
    },

    toggle_type_search: function(update_field) {
        var self = this;
        self.update_extended_search_info(
            $('type_search'), $('type_search_info'));
        MochiKit.DOM.toggleElementClass(
            'hidden', 'type_search', 'type_search_info');
        MochiKit.DOM.toggleElementClass(
            'unfolded', 'type_search_button');
        if (update_field) {
            var field = $('zeit-find-search-form')['type_search_expanded'];
            if (field.value) {
                field.value = '';
            } else {
                field.value = 'expanded';
            }
            self.search_result.render();
        }
    },

    toggle_extended_search: function(update_field) {
        var self = this;
        self.update_extended_search_info(
            $('extended_search'), $('extended_search_info'));
        MochiKit.DOM.toggleElementClass(
            'hidden', 'extended_search', 'extended_search_info');
        MochiKit.DOM.toggleElementClass(
            'unfolded', 'extended_search_button');
        if (update_field) {
            var field = $('zeit-find-search-form')['extended_search_expanded'];
            if (field.value) {
                field.value = '';
            } else {
                field.value = 'expanded';
            }
            self.search_result.render();
        }
    },

    update_extended_search_info: function(form_node, info_node) {
        var self = this;
        info_node.innerHTML = '';
        forEach($('zeit-find-search-form').elements, function(element) {
            if (!MochiKit.DOM.isChildNode(element, form_node)) {
                return
            }
            var value = null;
            var title = null;
            if (element.nodeName == 'SELECT') {
                if (element.selectedIndex == -1) {
                    element.selectedIndex = 0;
                }
                var option = element.options[element.selectedIndex];
                title = option.text;
                value = option.value;
            } else if (element.nodeName == 'INPUT') {
                if (element.type == 'checkbox') {
                    if (element.checked) {
                        var label  = jQuery('label[for="' + element.id + '"]');
                        if (label.length != 1) {
                            return;
                        }
                        value = element.value;
                        title = label[0].textContent;
                    }
                } else if (element.type == 'text'
                           && element.name != 'fulltext') {
                    value = element.value;
                    title = value;
                }
            }
            var default_value = element.getAttribute('default');
            if (title && value != default_value) {
                var css_class = 'info-' + element.name;
                info_node.appendChild(SPAN({'class': css_class}, title));
            }
        });
    },

    toggle_result_filters: function(update_field) {
        var self = this;
        MochiKit.DOM.toggleElementClass(
            'unfolded', 'result_filters_button');
        if (update_field) {
            var field = $('zeit-find-search-form')['result_filters_expanded'];
            if (field.value) {
                field.value = '';
            } else {
                field.value = 'expanded';
            }
            self.search_result.render();
        }

        if ($('result_filters_data')) {
            $('result_filters').innerHTML = '';
        } else  {
            self.result_filters.render();
        }
    },
    search_form_parameters: function() {
        var self = this;
        var qs = MochiKit.Base.queryString($('search_form'));
        return qs
    },

});


zeit.find.init_full_search = function(submit_on_pageload) {
    if (isUndefined(submit_on_pageload)) {
        submit_on_pageload = true;
    }

    // Make available for tests
    zeit.find._search = new zeit.find.Search(submit_on_pageload);
    jQuery('#cp-search').append('<div id="search_form"></div>');
    zeit.find._search.render();
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
            var toggle_favorited = jQuery('.toggle_favorited', entry)[0];
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
            var date_filter = jQuery('.date_filter', entry)[0];
            self.events.push(MochiKit.Signal.connect(
                date_filter, 'onclick', function(e) {
                    from_field.value = start_date;
                    until_field.value = end_date;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));

            var volume_year = lookup('volume_year');
            var volume_year_filter = jQuery('.volume_year_filter', entry)[0];
            self.events.push(MochiKit.Signal.connect(
                volume_year_filter, 'onclick', function(e) {
                    volume_year_field.value = volume_year;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));

            var topic = lookup('topic');
            var topic_filter = jQuery('.topic_filter', entry)[0];
            self.events.push(MochiKit.Signal.connect(
                topic_filter, 'onclick', function(e) {
                    topic_field.value = topic;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));

            jQuery('.author_filter', entry).each(function(i, author_filter) {
                var author_lookup = jsontemplate.get_node_lookup(
                    data, author_filter);
                var author = author_lookup('@');
                self.events.push(MochiKit.Signal.connect(
                    author_filter, 'onclick', function(e) {
                        author_field.value = author;
                    MochiKit.Signal.signal(window, 'zeit.find.update-search');
                }));
            });

            jQuery('.range', entry).each(function(i, range) {
                self.events.push(MochiKit.Signal.connect(
                    range, 'onclick', function(e) {
                    if (range.getAttribute('href') == '#') {
                        e.stop();
                    }
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
