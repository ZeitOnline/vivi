// Copyright (c) 2007-2009 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.LightboxForm = Class.extend({
    // Javascript support for forms in a light box

    construct: function(url, container) {
        // URL: URL of the form to load
        if (isUndefinedOrNull(container)) {
            container = $('body');
        }
        var self = this;
        self.container = container;
        self.url = url;
        self.events = [];
        self.lightbox = this.create_lightbox();
        self.content_box = this.lightbox.content_box;
        this.events.push(
            connect(this.content_box, 'onclick', this, 'handle_click'));
        this.events.push(
            connect(window, 'zeit.cms.LightboxReload', function(event) {
                self.loading();
            }));
        this.events.push(
            MochiKit.Signal.connect(
                this.lightbox, 'before-close', this, 'close'));
        self.reload();
    },

    create_lightbox: function() {
        return new gocept.Lightbox(this.container, {
            use_ids: false
        });
    },

    reload: function() {
        var self = this;
        var d = self.lightbox.load_url(self.url);
        d.addCallback(
            function(result) {
                self.post_process_html();
                return result;
            });
        return d
    },

    close: function() {
        // Close the lightbox and unregister everything.
        forEach(this.events, function(ident) {
            MochiKit.Signal.disconnect(ident);
        });
        this.lightbox.close();
    },

    handle_click: function(event) {
        var target = event.target()
        if (target.nodeName != 'INPUT')
            return
        if (target.type != 'button')
            return
        if (! hasElementClass(target, 'submit'))
            return
        this.handle_submit(target.name);
        event.stop();
    },

    handle_submit: function(action) {
        var self = this;

        // collect data
        var elements = filter(
            function(element) {
                return (element.type != 'button')
            }, this.form.elements);

        var data = map(function(element) {
                if ((element.type == 'radio' || element.type == 'checkbox')
                    && !element.checked) {
                    return
                }
                return element.name + "=" + encodeURIComponent(element.value)
            }, elements);
        data.push(action + '=clicked')
        data = data.join('&');
        var submit_to = this.form.getAttribute('action');

        // clear box with loading message
        this.loading();

        var d = doXHR(submit_to, {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded'},
            'sendContent': data});
        d.addCallbacks(
            function(result) {
                MochiKit.Signal.disconnectAll(self.form);
                self.content_box.innerHTML = result.responseText;
                if (action.indexOf('form.actions.') != 0) {
                    // This was no action. No error could have been generated.
                    // Also the form is not done, yet.
                    return result;
                }
                var errors = getFirstElementByTagAndClassName(
                    'ul', 'errors', self.content_box)
                if (errors != null) {
                    return result;
                }
                var next_url_node = getFirstElementByTagAndClassName(
                    'span', 'nextUrl', self.content_box);
                if (next_url_node == null) {
                    return result;
                }
                window.location = next_url_node.textContent;
                return null;
            },
            function(error) {
                logError(error.req.status, error.req.statusText);
                var parser = new DOMParser()
                var doc = parser.parseFromString(
                    error.req.responseText, "text/xml");
                document.firstChild.nextSibling.innerHTML = doc.firstChild.nextSibling.innerHTML;
            });
        d.addCallback(function(result) {
            if (result === null) {
                return null;
            }
            self.post_process_html();
            return result;
        });
        return d;
    },

    loading: function(message) {
        if (typeof message == 'undefined') {
            message = 'Loading ...';
        }
        this.content_box.innerHTML = 'Loading ...';
    },

    post_process_html: function() {
        var self = this;
        form = MochiKit.DOM.getFirstElementByTagAndClassName(
            'form', null, self.content_box);
        self.rewire_submit_buttons(form);
        self.eval_javascript_tags();
    },

    rewire_submit_buttons: function(form) {
        // Change all submits to buttons to be able to handle them in
        // java script
        var self = this;
        self.form = form;
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
                'input', null, self.content_box),
            function(button) {
                if (button.type == 'submit') {
                    button.type = 'button';
                    addElementClass(button, 'submit');
                }
            });
        if (self.form != null) {
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
            'SCRIPT', null, self.content_box),
            function(script) {
                eval(script.text);
            });
    },
});

zeit.cms.lightbox_form = function(url) {
    new zeit.cms.LightboxForm(url);
}
