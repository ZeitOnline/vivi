zeit.wysiwyg.ReferenceDialog = zeit.wysiwyg.Dialog.extend({

    construct: function() {
        var self = this;
        arguments.callee.$.construct.call(self);

        var browse_url = oPage.context_url + '/@@default-browsing-location';
        new ObjectReferenceWidget(
            'select-item', browse_url, self.browse_filter, false);
    },

    validate: function() {
        var self = this;
        var unique_id = $('href').value;
        if (! unique_id) {
            alert('Die URL wird benötigt.');
            return false;
        } else {
            return true;
        }
    },

    update: function() {
        var self = this;
        self.set_value('href', self.id_to_url($('href').value));
    },

    create: function() {
        var self = this;
        var div = DIV({'class': 'inline-element ' + self.container_class},
            DIV({'class': 'href'}));
        self.create_element(div);
        return div;
    },

    id_to_url: function(unique_id) {
        return unique_id
    },

    url_to_id: function(url) {
        return url
    },
});


zeit.wysiwyg.InfoboxDialog = zeit.wysiwyg.ReferenceDialog.extend({
    construct: function() {
        var self = this;
        self.container_class = 'infobox';
        self.browse_filter = 'zeit.content.infobox';
        arguments.callee.$.construct.call(self);
        $('href').value = self.get_value('href');
    },
});


zeit.wysiwyg.TimelineDialog = zeit.wysiwyg.ReferenceDialog.extend({
    construct: function() {
        var self = this;
        self.container_class = 'timeline';
        self.browse_filter = 'zeit.content.infobox';
        arguments.callee.$.construct.call(self);
        $('href').value = self.get_value('href');
    },
});


zeit.wysiwyg.PortraitboxDialog = zeit.wysiwyg.ReferenceDialog.extend({
    construct: function() {
        var self = this;
        self.container_class = 'portraitbox';
        self.browse_filter = 'zeit.content.portraitbox';
        arguments.callee.$.construct.call(self);
        $('href').value = self.get_value('href');
        $('layout').value = self.get_value('layout');
    },

    update: function() {
        var self = this;
        arguments.callee.$.update.call(self);
        self.set_value('layout', $('layout').value);
    },

    create: function() {
        var self = this;
        var container = arguments.callee.$.create.call(self);
        container.appendChild(DIV({'class': 'layout'}));
        return container;
    },

});


zeit.wysiwyg.GalleryDialog = zeit.wysiwyg.ReferenceDialog.extend({

    construct: function() {
        var self = this;
        self.container_class = 'gallery';
        self.browse_filter = 'zeit.content.gallery';
        arguments.callee.$.construct.call(self);
        $('href').value = self.get_value('href');
    },
});


zeit.wysiwyg.ImageDialog = zeit.wysiwyg.ReferenceDialog.extend({

    construct: function() {
        var self = this;
        self.browse_filter = 'images';
        arguments.callee.$.construct.call(self);

        MochiKit.Signal.connect('href', 'onchange', function(event) {
            var image = $('href');
            var preview = $('preview');
            var unique_id = image.value;
            preview.innerHTML = ''
            if (unique_id) {
                preview.appendChild(IMG({'src': self.id_to_url(unique_id)}));
            }
        });

        if (!isNull(self.container)) {
            $('href').value = self.url_to_id(self.container.src);
            $('layout').value = self.container.getAttribute('title');
            MochiKit.Signal.signal('href', 'onchange');
        }

        MochiKit.Signal.connect(
            $$('input[name="selectArticleImage"]')[0], 'onclick',
            self, self.load_article_image);

    },

    id_to_url: function(unique_id) {
        return unique_id.replace(
            'http://xml.zeit.de',
            zeit.cms.get_application_url() + '/repository');
    },

    url_to_id: function(url) {
        return url.replace(
            zeit.cms.get_application_url() + '/repository',
            'http://xml.zeit.de');
    },

    get_container: function() {
        var self = this;
        var img = oEditor.FCKSelection.GetSelectedElement();
        if (img === null || img.nodeName != 'IMG') {
            return null;
        }
        return img;
    },

    update: function() {
        var self = this;
        self.container.src = self.id_to_url($('href').value);
        self.container.setAttribute('title', $('layout').value);
    },

    create: function() {
        var self = this;
        var img = IMG();
        FCK.InsertElement(img);
        return img;
    },

    load_article_image: function() {
        var self = this;
        var base_url = oEditor.parent.location.href.split(
            '/').slice(0, -1).join('/');
        var d = MochiKit.Async.loadJSONDoc(base_url + '/@@images.json');
        d.addCallbacks(
            function(result) {
                // find the right image: 540x…
                var unique_id = null;
                forEach(result['images'], function(image) {
                    var name = image.split('/').slice(-1)[0];
                    if (name.search('540x') >= 0) {
                        unique_id = image;
                        throw MochiKit.Iter.StopIteration;
                    }
                });
                if (!isNull(unique_id)) {
                    $('href').value = unique_id;
                    MochiKit.Signal.signal('href', 'onchange');
                }
            },
            function(error) {
                log("Could not load images", error);
                alert("Could not load images.");
            }
        );
        
    },

});
