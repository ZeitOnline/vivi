zeit.content.cp.TeaserDrag = zeit.edit.context.ContentActionBase.extend({

    __name__: 'zeit.content.cp.TeaserDrag',
    context: zeit.edit.context.Editor,

    connect: function() {
        var self = this;
        jQuery('div.block.type-teaser').each(function(i, teaser) {
            var text =
                MochiKit.DOM.getFirstElementByTagAndClassName(
                    'div', 'teaser', teaser);
            if (isNull(text)) {
                return;
            }
            var image = jQuery('.teaser-contents > img', teaser);
            if (image.length) {
                image = image[0];
            } else {
                image = null;
            }
            text.removeFromBlock = teaser.id;
            self.dnd_objects.push(
                zeit.cms.createDraggableContentObject(text, {
                    scroll: 'cp-content-inner'
                }));
            self.dnd_objects.push(
                zeit.cms.createDraggableContentObject(text, {
                    handle: image,
                    scroll: 'cp-content-inner'
                }));
        });

    }

});

(function() {
    var ident = MochiKit.Signal.connect(
        window, 'script-loading-finished', function() {
            MochiKit.Signal.disconnect(ident);
            if (! zeit.cms.in_cp_editor()) {
                return;
            }
            zeit.content.cp.teaser_drag = new zeit.content.cp.TeaserDrag();
        });
}());
