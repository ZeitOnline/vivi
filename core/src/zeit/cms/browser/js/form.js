(function($) {

zeit.cms.SubPageForm = gocept.Class.extend({

    construct: function(url, container) {
        var self = this;
        self.container = container;
        self.url = url;
        self.events = [];
        self.bind(self.container, 'click', self.handle_click);
        self.bind(self.container, 'submit', self.submit_via_js);
        self.reload();
    },

    bind: function(target, event, handler) {
        var self = this;
        handler = MochiKit.Base.bind(handler, self);
        self.events.push([target, event, handler]);
        $(target).bind(event, handler);
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        // XXX duplicated from gocept.Lightbox.load_url
        var d = MochiKit.Async.doSimpleXMLHttpRequest(self.url);
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
                $(self.container).trigger_fragment_ready();
                MochiKit.Signal.signal(self, 'after-reload');
                $(self.container).removeClass('busy');
                return result;
            });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
        return d;
    },

    close: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'close');
        while(self.events.length) {
            var item = self.events.pop();
            $(item[0]).unbind(item[1], item[2]);
        }
    },

    handle_click: function(event) {
        var self = this;
        var target = event.target;

        if (target.nodeName == 'INPUT' &&
            target.type == 'button' &&
            $(target).hasClass('submit')) {
            self.handle_submit(target.name);
            event.stopPropagation();  // suppress browser submit behaviour
        }
    },

    submit_via_js: function(event) {
        var self = this;
        if (!isNull(self.form)) {
            self.handle_submit();
            return false;  // suppress browser submit behaviour
       }
    },

    handle_submit: function(action) {
        var self = this;

        // collect data
        var elements = filter(
            function(element) {
                return (element.type != 'button');
            }, self.form.elements);

        var data = map(function(element) {
                if ((element.type == 'radio' || element.type == 'checkbox') &&
                    !element.checked) {
                    return;
                }
                return element.name + "=" + encodeURIComponent(element.value);
            }, elements);
        if (isUndefinedOrNull(action)) {
            var button = $(self.container).find(
                '> .form-controls input').first();
            action = button.attr('name');
        }
        data.push(action + '=clicked');
        data = data.join('&');
        var submit_to = self.form.getAttribute('action');

        // clear box with loading message
        self.loading();

        var d = zeit.cms.locked_xhr(submit_to, {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded'},
            'sendContent': data});
        d.addCallbacks(
            MochiKit.Base.bind(self.replace_content, self),
            function(error) {
                logError(error.req.status, error.req.statusText);
                var parser = new DOMParser();
                var doc = parser.parseFromString(
                    error.req.responseText, "text/xml");
                document.firstChild.nextSibling.nextSibling.innerHTML = doc.firstChild.nextSibling.innerHTML;
            });
        d.addCallback(MochiKit.Base.bind(self.process_post_result, self));
        d.addCallback(function(result) {
            if (result === null) {
                return null;
            }
            // XXX this is the third place that calls post_process_html and
            // sends signals -- refactor! (#11270).
            self.post_process_html();
            $(self.container).trigger_fragment_ready();
            MochiKit.Signal.signal(window, 'changed', self);
            MochiKit.Signal.signal(self, 'after-reload');
            // Delaying the class remove somehow avoids flickering
            MochiKit.Async.callLater(
                0, function() { $(self.container).removeClass('busy'); });
            return result;
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
        return d;
    },

    replace_content: function(result) {
        var self = this;
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
        var errors = $(self.container).find('ul.errors');
        return (errors.length > 0);
    },

    get_next_url: function() {
        var self = this;
        var next_url_node = $(self.container).find('span.nextURL');
        if (! next_url_node.length) {
            return null;
        }
        return next_url_node[0].textContent;
    },

    loading: function(message) {
        var self = this;
        if (!isUndefinedOrNull(message)) {
            log('messssage', repr(message));
            self.container.innerHTML = message;
        }
        $(self.container).addClass('busy');
    },

    post_process_html: function() {
        var self = this;
        if (self.container.nodeName == 'FORM') {
            self.form = self.container;
        } else {
            self.form = $(self.container).find('form');
        }
        self.rewire_submit_buttons();
        zeit.cms.evaluate_js_and_css(
            self.container, function(code) { eval(code); });
    },

    rewire_submit_buttons: function() {
        // Change all submits to buttons to be able to handle them in
        // javascript
        var self = this;
        $(self.container).find('input[type="submit"]').each(function() {
            var button = $(this);
            // XXX jQuery refuses to change the ``type`` property, so we go
            // directly to the DOM node instead.
            this.type = 'button';
            button.addClass('submit');
        });
    }
});


// XXX Shouldn't we call this AutoSavingForm or something? At least InlineForm
// is consistent with zeit.edit where it is used. (Actually, the whole
// InlineForm stuff should be moved to zeit.cms, since it's independent from
// zeit.edit).
zeit.cms.InlineForm = zeit.cms.SubPageForm.extend({

    SUBMIT_DELAY_FOR_FOCUS: 0.01,
    focus_node: null,
    mouse_down: false,
    delay_submit: false,

    construct: function(url, container) {
        var self = this;
        arguments.callee.$.construct.call(self, url, container);
        // In general fields are saved, when they lose focus. But there
        // are various exceptions from the rule:
        //
        // - When the user switches from one field to the other: This is
        //   the obvious case.
        // - When the mouse is still down: The old field loses focus after
        //   mouse-down, but there are widgets containing buttons. The
        //   button actions are evaluated on click (that is after
        //   mouse-up). So special care must be taken to not submit while
        //   the mouse is down.
        // - Since we prevent saving while the mouse is down, chances are
        //   that we need to save on mouse up, when a field lost focus
        //   before.
        self.bind(self.container, 'change', self.mark_dirty);
        self.bind(self.container, 'focusin', self.store_focus);
        self.bind(self.container, 'focusout', function(event) {
            self.release_focus(event);

            // Don't submit if the focus is inside a *nested* SubPageForm;
            // the nested form *will* be submitted, which is enough.
            if ($(event.target).closest('form')[0] != self.container) {
                return;
            }

            if (self.is_input(event.target) && !self.mouse_down) {
                self.fire_submit();
            } else {
                self.delay_submit = true;  // delay until mouse up.
            }
        });
        self.bind(self.container, 'mousedown', function(event) {
            self.mouse_down = true;
        });
        self.bind(self.container, 'mouseup', function(event) {
            self.mouse_down = false;
            if (!self.is_input(event.target) &&
                self.delay_submit) {
                self.fire_submit();
            }
        });
    },

    reload: function() {
        // We don't need/support actual reloading. During construct, our
        // contents have already been rendered by the server, so we only need
        // to do the post-processing and send the appropriate signals.
        var self = this;
        self.post_process_html();
        $(self.container).trigger_fragment_ready();
        MochiKit.Signal.signal(self, 'after-reload');
    },

    handle_click: function(event) {
        var self = this;
        var target = event.target;

        arguments.callee.$.handle_click.call(self, event);

        if (target.nodeName == 'INPUT' && target.type == 'checkbox') {
            self.handle_submit();
        }
    },

    mark_dirty: function(event) {
        var self = this;
        var target = event.target;

        if (zeit.cms.in_array(
            target.nodeName, ['INPUT', 'TEXTAREA', 'SELECT'])) {
            $(target).closest('.field').addClass('dirty');
            if (target.nodeName == 'INPUT' && target.type == 'hidden') {
                self.handle_submit();
            }
        }
    },

    store_focus: function(event) {
        var self = this;
        if (self.is_input(event.target)) {
            self.focus_node = event.target;
        }
    },

    release_focus: function(event) {
        var self = this;
        self.focus_node = null;
    },

    fire_submit: function() {
        var self = this;
        self.delay_submit = false;
        MochiKit.Async.callLater(self.SUBMIT_DELAY_FOR_FOCUS, function() {
            // If a field of our form has the focus now, we don't want to
            // interrupt the user by saving.
            if (self.focus_node === null) {
                self.handle_submit();
            }
        });
    },

    is_input: function(node) {
        return zeit.cms.in_array(
            node.nodeName, ['INPUT', 'TEXTAREA', 'SELECT']);
    },


});

}(jQuery));
