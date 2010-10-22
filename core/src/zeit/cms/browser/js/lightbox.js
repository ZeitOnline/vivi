// Copyright (c) 2007-2010 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.SubPageForm = Class.extend({


    construct: function(url, container, options) {
        var self = this;
        // initialize defaults
        self.clear_on_load = true;
        // update options
        MochiKit.Base.update(self, options);
        self.container = container;
        self.url = url;
        self.events = [];
        self.events.push(
            MochiKit.Signal.connect(
                self.container, 'onclick', self, self.handle_click));
        self.reload();
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        // XXX duplicated from gocept.Lightbox.load_url
        var d = doSimpleXMLHttpRequest(self.url);
        d.addCallbacks(
            function(result) {
                return result.responseText;
            },
            function(error) {
                return "There was an error loading the content: " + error;
            });
        d.addCallback(
            function(result) {
                self.container.innerHTML = result;
                self.post_process_html();
                MochiKit.Signal.signal(self, 'after-reload');
                MochiKit.DOM.removeElementClass(self.container, 'busy');
                return result;
            });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
        return d
    },

    close: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'close');
        while(self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        };
    },

    handle_click: function(event) {
        var self = this;

        var target = event.target()
        if (target.nodeName != 'INPUT')
            return
        if (target.type != 'button')
            return
        if (! hasElementClass(target, 'submit'))
            return
        self.handle_submit(target.name);
        event.stop();
    },

    handle_submit: function(action) {
        var self = this;

        // collect data
        var elements = filter(
            function(element) {
                return (element.type != 'button')
            }, self.form.elements);

        var data = map(function(element) {
                if ((element.type == 'radio' || element.type == 'checkbox')
                    && !element.checked) {
                    return
                }
                return element.name + "=" + encodeURIComponent(element.value)
            }, elements);
        data.push(action + '=clicked')
        data = data.join('&');
        var submit_to = self.form.getAttribute('action');

        // clear box with loading message
        self.loading();

        var d = doXHR(submit_to, {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded'},
            'sendContent': data});
        d.addCallbacks(
            MochiKit.Base.bind(self.replace_content, self),
            function(error) {
                logError(error.req.status, error.req.statusText);
                var parser = new DOMParser()
                var doc = parser.parseFromString(
                    error.req.responseText, "text/xml");
                document.firstChild.nextSibling.innerHTML = doc.firstChild.nextSibling.innerHTML;
            });
        d.addCallback(MochiKit.Base.bind(self.process_post_result, self));
        d.addCallback(function(result) {
            if (result === null) {
                return null;
            }
            self.post_process_html();
            MochiKit.Signal.signal(self, 'after-reload');
            // Delaying the class remove somehow avoids flickering
            MochiKit.Async.callLater(0,
                MochiKit.DOM.removeElementClass, self.container, 'busy');
            return result;
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
        return d;
    },

    replace_content: function(result) {
        var self = this;
        if (self.form !== self.container) {
            MochiKit.Signal.disconnectAll(self.form);
        }
        self.container.innerHTML = result.responseText;
        return result;
    },

    process_post_result: function(result) {
        var self = this;
        if (self.has_errors()) {
            return result;
        }
        var next_url = self.get_next_url();
        if (isNull(next_url)) {
            return result;
        }
        window.location = next_url;
        return null;
    },

    has_errors: function(result) {
        var self = this;
        var errors = getFirstElementByTagAndClassName(
            'ul', 'errors', self.container);
        return (errors != null);
    },

    get_next_url: function() {
        var self = this;
        var next_url_node = getFirstElementByTagAndClassName(
            'span', 'nextURL', self.container);
        if (isNull(next_url_node)) {
            return null;
        }
        return next_url_node.textContent;
    },

    loading: function(message) {
        var self = this;
        if (!isUndefinedOrNull(message)) {
            log('messssage', repr(message));
            self.container.innerHTML = message;
        }
        MochiKit.DOM.addElementClass(self.container, 'busy');
    },

    post_process_html: function() {
        var self = this;
        if (self.container.nodeName == 'FORM') {
            self.form = self.container;
        } else {
            self.form = MochiKit.DOM.getFirstElementByTagAndClassName(
                'form', null, self.container);
        }
        self.rewire_submit_buttons();
        self.eval_javascript_tags();
    },

    rewire_submit_buttons: function() {
        // Change all submits to buttons to be able to handle them in
        // java script
        var self = this;
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
                'input', null, self.container),
            function(button) {
                if (button.type == 'submit') {
                    button.type = 'button';
                    addElementClass(button, 'submit');
                }
            });
        if (!isNull(self.form) && self.form !== self.container) {
            self.events.push(MochiKit.Signal.connect(
                self.form, 'onsubmit', function(event) {
                // prevent accidental submit
                event.stop()
            }));
        }
    },

    eval_javascript_tags: function() {
        var self = this;
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
            'SCRIPT', null, self.container),
            function(script) {
                eval(script.text);
            });
    },
});


zeit.cms.LightboxForm = zeit.cms.SubPageForm.extend({

    construct: function(url, container) {
        var self = this;
        if (isUndefinedOrNull(container)) {
            container = $('body');
        }
        self.lightbox = self.create_lightbox(container);
        arguments.callee.$.construct.call(self, url, self.lightbox.content_box);
        self.events.push(
            connect(window, 'zeit.cms.LightboxReload', function(event) {
                self.loading();
            }));
        self.events.push(
            MochiKit.Signal.connect(
                self.lightbox, 'before-close', self, self.close));
    },

    create_lightbox: function(container) {
        var self = this;
        return new gocept.Lightbox(container, {
            use_ids: false
        });
    },

    reload: function() {
        var self = this;
        var d = self.lightbox.load_url(self.url);
        d.addCallback(function(result) {
            self.post_process_html();
            return result;
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
        return d
    },

    close: function() {
        var self = this;
        arguments.callee.$.close.call(self);
        self.lightbox.close();
    },
});


zeit.cms.lightbox_form = function(url) {
    new zeit.cms.LightboxForm(url);
}
