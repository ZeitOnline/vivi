// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$


zeit.cms.LightboxForm = Class.extend({
    // Javascript support for forms in a light box

    construct: function(url) {
        // URL: URL of the form to load
        //
        var othis = this;
        this.lightbox = new gocept.Lightbox($('body'));
        this.content_box = this.lightbox.content_box;
        connect(this.content_box, 'onclick', this, 'handle_click');
        connect(window, 'zeit.cms.LightboxReload', function(event) {
            othis.loading();
        });

        var d = this.lightbox.load_url(url);
        d.addCallback(
            function(result) {
                // Change all submits to buttons to be able to handle them in
                // java script
                forEach(
                    getElementsByTagAndClassName(
                        'input', 'button', othis.content_box),
                    function(button) {
                        button.type = 'button';
                    });
                othis.form = $('lightbox.form');
                if (othis.form != null) {
                    connect(othis.form, 'onsubmit', function(event) {
                        // prevent accidential submit
                        event.stop()
                    });
                }
                
                // check for javascript
                forEach(
                    getElementsByTagAndClassName('SCRIPT', null,
                                                 othis.content_box),
                    function(script) {
                        eval(script.text);
                    });
                return result;
            });

    },

    handle_click: function(event) {
        var target = event.target()
        if (target.nodeName != 'INPUT')
            return
        if (target.type != 'button')
            return
        if (target.name.indexOf('form.actions.') == 0) {
            this.handle_submit(target.name);
            event.stop();
        }

    },

    handle_submit: function(action) {
        var othis = this;

        // collect data
        var elements = filter(
            function(element) {
                return (element.type != 'button')
            }, this.form.elements);

        var data = map(function(element) {
                element = $(element.id);
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
                othis.content_box.innerHTML = result.responseText;
                var errors = getFirstElementByTagAndClassName(
                    'ul', 'errors', othis.content_box)
                if (errors != null)
                    return;
                var next_url_node = getFirstElementByTagAndClassName(
                    'span', 'nextUrl', othis.content_box);
                if (next_url_node == null)
                    return
                window.location = next_url_node.textContent;
            },
            function(error) {
                logError(error.req.status, error.req.statusText);
                var parser = new DOMParser()
                var doc = parser.parseFromString(
                    error.req.responseText, "text/xml");
                document.firstChild.nextSibling.innerHTML = doc.firstChild.nextSibling.innerHTML;
            });
    },

    loading: function(message) {
        if (typeof message == 'undefined') {
            message = 'Loading ...';
        }
        this.content_box.innerHTML = 'Loading ...';
    },

});

zeit.cms.lightbox_form = function(url) {
    new zeit.cms.LightboxForm(url);
}
