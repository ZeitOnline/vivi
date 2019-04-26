// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt

gocept.Lightbox = gocept.Class.extend({

    default_options: {
        use_ids: true
    },

    construct: function(parent_element, option_args) {
        var options = MochiKit.Base.clone(this.default_options);
        if (!isUndefinedOrNull(option_args)) {
            MochiKit.Base.update(options, option_args);
        }

        this.parent_element = parent_element;
        this.shade = DIV({'class': 'lightbox-shade'});
        this.header = DIV({'class': 'lightbox-header'});
        this.closebutton = A({'href': '#',
                              'title': 'Close',
                              'class': 'CloseButton'});
        this.content_box = DIV({'class': 'lightbox'});

        if (options.use_ids) {
            forEach([this.shade, this.header, this.content_box],
                    function(element) {
                        element.id = element.getAttribute('class');
            });
        }

        MochiKit.DOM.appendChildNodes(this.header, this.closebutton);
        MochiKit.DOM.appendChildNodes(
            this.parent_element, this.shade, this.header, this.content_box);
        this.events = [];
        this.events.push(
            MochiKit.Signal.connect(
                this.closebutton, 'onclick', this, this.close));
        this.events.push(
            MochiKit.Signal.connect(
                this.shade, 'onclick', this, this.close));
    },

    close: function() {
        MochiKit.Signal.signal(this, 'before-close');
        while (this.events.length) {
            MochiKit.Signal.disconnect(this.events.pop());
        }

        forEach([this.shade, this.header, this.content_box],
                function(element) {
                    MochiKit.Signal.disconnectAll(element);
                    if (!isNull(element.parentNode)) {
                        MochiKit.DOM.removeElement(element);
                    }
        });
    },

    load_url: function(url, query) {
        if (query == undefined) {
            query = {};
        }

        var othis = this;
        if (this.innerHTML == "") {
            this.replace_content("Loading ...");
        }
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url, query);
        d.addCallbacks(
            function(result) {
                return result.responseText;
            },
            function(error) {
                return "There was an error loading the content: " + error;
            });
        d.addCallback(function(result) {
            othis.replace_content(result);
            return result;
        });
        return d;
    },

    replace_content: function(new_html) {
        this.content_box.innerHTML = new_html;
    }

});


zeit.cms.LightboxForm = zeit.cms.SubPageForm.extend({

    construct: function(url, container) {
        var self = this;
        if (isUndefinedOrNull(container)) {
            container = jQuery('body')[0];
        }
        self.lightbox = self.create_lightbox(container);
        arguments.callee.$.construct.call(self, url, self.lightbox.content_box);
        self.mochi_events = [];
        self.mochi_events.push(
            MochiKit.Signal.connect(
                window, 'zeit.cms.LightboxReload', function(event) {
                self.set_busy();
            }));
        self.mochi_events.push(
            MochiKit.Signal.connect(
                self.lightbox, 'before-close', self, self.close));
        zeit.cms.current_lightbox = self;
    },

    create_lightbox: function(container) {
        return new gocept.Lightbox(container, {
            use_ids: false
        });
    },

    reload: function() {
        var self = this;
        var d = self.lightbox.load_url(self.url);
        d.addCallback(function(result) {
            self.post_process_html();
            jQuery(self).trigger_fragment_ready();
            return result;
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
        return d;
    },

    close: function() {
        var self = this;
        arguments.callee.$.close.call(self);
         while(self.mochi_events.length) {
             MochiKit.Signal.disconnect(self.mochi_events.pop());
         }
        self.lightbox.close();
        zeit.cms.current_lightbox = null;
    }
});


zeit.cms.lightbox_form = function(url) {
    new zeit.cms.LightboxForm(url);
};


zeit.cms.LoadInLightbox = function(context_element) {
    var url = context_element.getAttribute('href');
    return new zeit.cms.LightboxForm(url);
};
