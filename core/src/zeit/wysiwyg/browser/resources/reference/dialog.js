zeit.wysiwyg.ImageDialog = zeit.wysiwyg.Dialog.extend({

    get_container: function() {
        var self = this;
        var img = oEditor.FCKSelection.GetSelectedElement();
        if (img === null || img.nodeName != 'IMG') {
            return null;
        }
        return img;
    },

    construct: function() {
        var self = this;
        arguments.callee.$.construct.call(self);

        var browse_url = oPage.context_url + '/@@default-browsing-location';
        new ObjectReferenceWidget('select-image', browse_url, 'images', false);

        MochiKit.Signal.connect('image', 'onchange', function(event) {
            var image = $('image');
            var preview = $('preview');
            var unique_id = image.value;
            preview.innerHTML = ''
            if (unique_id) {
                preview.appendChild(IMG({'src': self.id_to_url(unique_id)}));
            }
        });

        if (self.container !== null) {
            $('image').value = url_to_id(self.container);
            MochiKit.Signal.signal('image', 'onchange');
        }
    },

    validate: function() {
        var self = this;
        var unique_id = $('image').value;
        if (! unique_id) {
            alert('Die Bild-URL wird benötigt.');
            return false;
        } else {
            return true;
        }
    },

    update: function() {
        var self = this;
        self.container.src = self.id_to_url($('image').value);
    },

    create: function() {
        var self = this;
        var img = IMG();
        FCK.InsertElement(img);
        return img;
    },

    id_to_url: function(unique_id) {
        return unique_id.replace(
            'http://xml.zeit.de', oPage.application_url + '/repository');
    },

    url_to_id: function(url) {
        return url.replace(
            oPage.application_url + '/repository', 'http://xml.zeit.de');
    },
});


zeit.wysiwyg.dialog_class = zeit.wysiwyg.ImageDialog;
