(function() {

    var nbsp = ' ';

    zeit.cms.declare_namespace('zeit.cms.tagging');

    zeit.cms.tagging.Widget = gocept.Class.extend({

        construct: function(id, keywords_shown, tags) {
            var self = this;
            self.id = id;
            self.keywords_shown = keywords_shown;
            self.list = $(id + ".list");
            self.empty_marker = jQuery(
                'input[name="' + id + '-empty-marker"]')[0];
            self.populate_keywords(tags);
            MochiKit.Signal.connect(id, 'onclick', self, self.handle_click);
        },

        _sortable: function() {
            var self = this;
            jQuery(self.list).sortable({
                items: '> li',
                axis: 'y',
                scroll: false,
                update: function(event, ui) {
                    jQuery(self.empty_marker).trigger('change');
                }
            });
        },

        handle_click: function(event) {
            var self = this;
            if (event.target().nodeName == 'A' &&
                event.target().hash == '#update_tags') {
                event.stop();
                self.update_tags();
            }
        },

        populate_keywords: function(tags) {
            var self = this;
            var id;
            self.list.innerHTML = '';
            for(var i=0; i<tags.length; i++) {
                id = self.id + "." + i;
                tag = tags[i];
                var input_attrs = {
                    name: self.id,
                    id: id,
                    type: 'checkbox',
                    value: tag.code};
               if (!tag.disabled) {
                    input_attrs['checked'] = 'checked';
                }
                var attrs = {};
                if (i < self.keywords_shown) {
                    attrs['class'] = 'shown';
                } else {
                    attrs['class'] = 'not-shown';
                }
                self.list.appendChild(LI(
                    attrs, LABEL({'class': 'icon'}, INPUT(input_attrs)),
                    tag.label));
            }
            jQuery(self.list).css('width', jQuery(self.list).width() + 'px');
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
        }

    });

})();
