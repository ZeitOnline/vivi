// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(window, "onload", function(event) {
    var table = getElementsByTagAndClassName('table', 'contentListing')[0];
    forEach(table.rows, function(row) {
        if (row.cells[0].nodeName == 'TD') {
            new Draggable(row, {
                starteffect: null,
                endeffect: null});
        }
    });
});


zeit.cms.ContentRenamer = Class.extend({

    construct: function(url) {
        var othis = this;
        this.lightbox = new gocept.Lightbox($('body'));
        connect(this.lightbox.content_box, 'onclick', this, 'handleClick');
        var d = this.lightbox.load_url(url);
        var content_box = this.lightbox.content_box;
        d.addCallback(
            function(result) {
                // Change all submits to buttons to be able to handle them in
                // java script
                forEach(
                    getElementsByTagAndClassName(
                        'input', 'button', content_box),
                    function(button) {
                        button.type = 'button';
                    });
                othis.form = $('rename.form');
                connect(othis.form, 'onsubmit', function(event) {
                    // prevent accidential submit
                    event.stop()
                });
                return result;
            });

    },


    handleClick: function(event) {
        var target = event.target()
        if (target.nodeName != 'INPUT')
            return
        if (target.name == 'form.actions.rename') {
            var action = 'action_' + target.name.substring(13);
            var func = bind(action, this);
            func();
            event.stop();
        }

    },

    action_rename: function() {
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
        data.push('form.actions.rename=Rename')
        data = data.join('&');
        var action = this.form.getAttribute('action');

        // clear box with loading message
        this.lightbox.content_box.innerHTML = 'Loading ...'

        var d = doXHR(action, {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded'},
            'sendContent': data});
        d.addCallbacks(
            function(result) {
                othis.lightbox.content_box.innerHTML = result.responseText;
                var errors = getFirstElementByTagAndClassName(
                    'ul', 'errors', othis.lightbox.content_box)
                if (errors != null)
                    return;
                var next_url_node = getFirstElementByTagAndClassName(
                    'span', 'nextUrl', othis.lightbox.content_box);
                othis.lightbox.content_box.innerHTML = 'Loading ...';
                window.location = next_url_node.textContent;
            },
            alert);
    },

});

zeit.cms.rename_content = function(url) {
    new zeit.cms.ContentRenamer(url);
}
