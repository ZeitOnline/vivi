(function($) {
"use strict";

var nbsp = ' ';

zeit.cms.declare_namespace('zeit.cms.tagging');

zeit.cms.tagging.Widget = gocept.Class.extend({

    construct: function(id, keywords_shown) {
        var self = this;
        self.id = id;
        self.element = document.getElementById(id + '.wrapper');
        self.keywords_shown = keywords_shown;
        self.list = document.getElementById(id + '.list');
        self.data = document.getElementById(id);
        self.autocomplete = document.getElementById(id + '.add');
        self.populate_keywords($.parseJSON($(self.data).val()));
        MochiKit.Signal.connect(
            id + '.wrapper', 'onclick', self, self.handle_click);
        self._initialize_autocomplete();
        self._initialize_sortable();
    },


    _initialize_autocomplete: function() {
        var self = this;
        $(self.autocomplete).autocomplete({
            source: self.autocomplete.getAttribute('cms:autocomplete-source'),
            minLength: 3,
            focus: function(event, ui) {
                $(self.autocomplete).val(ui.item.label);
                return false;
            },
            select: function(event, ui) {
                self.add(ui.item.value, ui.item.label, /*pinned=*/true,
                         /*position=*/'start');
                $(self.autocomplete).val('');
                return false;
            },
            appendTo: self.element
        });
    },

    _initialize_sortable: function() {
        var self = this;
        $(self.list).sortable({
            items: '> li',
            axis: 'y',
            scroll: false,
            update: function(event, ui) {
                self._sync_json_widget_value();
                $(self.data).trigger('change');
            }
        });
    },

    handle_click: function(event) {
        var self = this;
        var method = event.target().getAttribute('cms:call');
        if (isNull(method)) {
            return;
        }

        method = self[method];
        method.call(self, event);
        event.stop();
    },

    to_json: function() {
        var self = this;
        var result = [];
        $('> li', self.list).each(function(i, el) {
            el = $(el);
            result.push({code: el.attr('cms:uniqueId'),
                         label: el.text(),
                         pinned: Boolean(el.find('.pinned').length)});
        });
        return result;
    },

    delete: function(event) {
        var self = this;
        $(event.target()).closest('li').remove();
        self._sync_json_widget_value();
        $(self.data).trigger('change');
    },

    add: function(code, label, pinned, position) {
        var self = this;
        self._add(code, label, pinned, position);
        self._sync_json_widget_value();
    },

    _add: function(code, label, pinned, position) {
        var self = this;
        if (isUndefined(position)) {
            position = 'end';
        }
        var pinned = pinned ? 'pinned' : 'toggle-pin';
        var item = LI(
            {'cms:uniqueId': code},
            SPAN({'class': 'icon delete', 'cms:call': 'delete'}),
            SPAN({'class': 'icon ' + pinned, 'cms:call': 'toggle_pinned'}),
            label);
        if (position === 'end') {
            $(self.list).append(item);
        } else {
            $(self.list).prepend(item);
        }
    },

    toggle_pinned: function(event) {
        var self = this;
        var icon = $(event.target());
        var currently_pinned = icon.hasClass('pinned');
        if (currently_pinned) {
            icon.removeClass('pinned');
            icon.addClass('toggle-pin');
        } else {
            icon.removeClass('toggle-pin');
            icon.addClass('pinned');
        }
        self._sync_json_widget_value();
        $(self.data).trigger('change');
    },

    populate_keywords: function(tags) {
        var self = this;
        $.each(tags, function(i, tag) {
            self._add(tag.code, tag.label, tag.pinned);
        });
        self._sync_json_widget_value();
    },

    update_tags: function() {
        var self = this;
        var d = MochiKit.Async.doXHR('@@update_tags', {method: 'POST'});
        MochiKit.DOM.addElementClass(self.list, 'busy');
        d.addCallback(function(result) {
            var json = MochiKit.Async.evalJSONRequest(result);
            self.list.innerHTML = '';
            self.populate_keywords(json.tags);
            self._initialize_sortable();
            return result;
        });
        d.addBoth(function(result_or_error) {
            MochiKit.DOM.removeElementClass(self.list, 'busy');
        });
    },

    _sync_json_widget_value: function() {
        var self = this;
        $('li', self.list).each(function (i, item) {
            if (i < self.keywords_shown) {
                $(item).addClass('shown');
                $(item).removeClass('not-shown');
            } else {
                $(item).removeClass('shown');
                $(item).addClass('not-shown');
            }
        });
        $(self.data).val(JSON.stringify(self.to_json()));
        $(self.list).css('width', $(self.list).width() + 'px');
    }

});

})(jQuery);
