(function($) {
"use strict";

var nbsp = ' ';

zeit.cms.declare_namespace('zeit.cms.tagging');

zeit.cms.tagging.Widget = gocept.Class.extend({

    construct: function(id, keywords_shown) {
        var self = this;
        self.id = id;
        self.keywords_shown = keywords_shown;
        self.list = document.getElementById(id + '.list');
        self.data = document.getElementById(id);
        self.populate_keywords($.parseJSON($(self.data).val()));
        MochiKit.Signal.connect(
            id + '.wrapper', 'onclick', self, self.handle_click);
    },

    _sortable: function() {
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
                         label: el.text()});
        });
        return result;
    },

    delete: function(event) {
        var self = this;
        $(event.target()).closest('li').remove();
        self._sync_json_widget_value();
        $(self.data).trigger('change');
    },

    populate_keywords: function(tags) {
        var self = this;
        var tag;
        self.list.innerHTML = '';
        for(var i=0; i<tags.length; i++) {
            tag = tags[i];
            var attrs = {'cms:uniqueId': tag.code};
            if (i < self.keywords_shown) {
                attrs['class'] = 'shown';
            } else {
                attrs['class'] = 'not-shown';
            }
            self.list.appendChild(LI(
                attrs, LABEL({'class': 'icon', 'cms:call': 'delete'}),
                tag.label));
        }
        self._sync_json_widget_value();
        $(self.list).css('width', $(self.list).width() + 'px');
        self._sortable();
    },

    update_tags: function() {
        var self = this;
        var d = MochiKit.Async.doXHR('@@update_tags', {method: 'POST'});
        MochiKit.DOM.addElementClass(self.list, 'busy');
        d.addCallback(function(result) {
            var json = MochiKit.Async.evalJSONRequest(result);
            self.populate_keywords(json.tags);
            return result;
        });
        d.addBoth(function(result_or_error) {
            MochiKit.DOM.removeElementClass(self.list, 'busy');
        });
    },

    _sync_json_widget_value: function() {
        var self = this;
        $(self.data).val(JSON.stringify(self.to_json()));
    }

});

})(jQuery);
