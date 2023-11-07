zeit.content.cp.TeaserDrag = zeit.edit.context.ContentActionBase.extend({

    __name__: 'zeit.content.cp.TeaserDrag',
    context: zeit.edit.context.Editor,

    connect: function() {
        var self = this;
        jQuery('div.block.type-teaser').each(function(i, teaser) {
            var text = MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'teaser', teaser);
            if (isNull(text)) {
                return;
            }
            var block_inner = MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'teaser-contents', teaser);
            self.dnd_objects.push(
                zeit.cms.createDraggableContentObject(text, {
                    scroll: 'cp-content-inner',
                    handle: block_inner
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
