(function() {

    var nbsp = ' ';

    zeit.cms.declare_namespace('zeit.cms.tagging');

    zeit.cms.tagging.Widget = gocept.Class.extend({

        construct: function(id) {
            var self = this;
            self.id = id;
            self.list = $(id + ".list");
            self._sortable();
            MochiKit.Signal.connect(id, 'onclick', self, self.handle_click);
            
        },

        _sortable: function() {
            var self = this;
            jQuery(self.list).sortable({
                items: '> li',
                axis: 'y'
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

        update_tags: function() {
            var self = this;
            var d = MochiKit.Async.doXHR('@@update_tags', {method: 'POST'});
            MochiKit.DOM.addElementClass(self.list, 'busy');
            d.addCallback(function(result) {
                var json = MochiKit.Async.evalJSONRequest(result);
                var id;
                self.list.innerHTML = '';
                for(var i=0; i<json.tags.length; i++) {
                    id = self.id + "." + i;
                    tag = json.tags[i];
                    var input_attrs = {
                        name: self.id,
                        id: id,
                        type: 'checkbox',
                        value: tag.code};
                   if (!tag.disabled) {
                        input_attrs['checked'] = 'checked';
                    }
                    self.list.appendChild(
                        LI({}, LABEL({},
                                     INPUT(input_attrs),
                                     nbsp, tag.label)));
                }
            self._sortable();
            return result;
            });
            d.addBoth(function(result_or_error) {
                MochiKit.DOM.removeElementClass(self.list, 'busy');
            });
        }

    });

})();
