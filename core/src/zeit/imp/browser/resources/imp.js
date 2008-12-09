// IMP

zeit.imp = {}

zeit.imp.Imp = Class.extend({

    construct: function() {
        this.image = $('imp-image');
        this.image_dragger = new MochiKit.DragAndDrop.Draggable(
            'imp-image-drag');
        this.load_image();
        MochiKit.Signal.connect(
            'imp-image-drag', 'onmousewheel', this, 'handle_mouse_wheel');

    },

    get_image_screen_dimensions: function() {
        return MochiKit.Style.getElementDimensions('imp-image-area');
    },

    load_image: function() {
        var dim = this.get_image_screen_dimensions();
        var query = MochiKit.Base.queryString({
            'width': dim.w,
            'height': dim.h});
        var image_url = window.context_url + '/@@imp-scaled?' + query;
        this.image.src = image_url; 
    },

    handle_mouse_wheel: function(event) {
        log('INFO', event);
    },

});

MochiKit.Signal.connect(window, 'onload', function() {
    new zeit.imp.Imp();
});
