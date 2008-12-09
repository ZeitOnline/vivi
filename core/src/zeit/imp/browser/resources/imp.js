// IMP

zeit.imp = {}

zeit.imp.Imp = Class.extend({

    construct: function() {
        this.zoom = 1;
        this.original_dimensions = new MochiKit.DOM.Dimensions(
            new Number($('imp-width').textContent),
            new Number($('imp-height').textContent));

        this.image = $('imp-image');
        this.image_dragger = new MochiKit.DragAndDrop.Draggable(
        'imp-image-drag', {'handle': $('imp-mask')});
        MochiKit.Signal.connect(
            'imp-image-area', 'onmousewheel', this, 'handle_mouse_wheel');
        this.load_image(this.original_dimensions);
        removeElementClass(this.image, 'loading');

    },

    get_image_dimensions: function() {
        return MochiKit.Style.getElementDimensions(this.image);
    },

    zoom_image: function() {
        var new_dim = new MochiKit.DOM.Dimensions(
            this.original_dimensions.w * this.zoom,
            this.original_dimensions.h * this.zoom);
        MochiKit.Style.setElementDimensions(this.image, new_dim);
    },


    load_image: function(dim) {
        var query_string = MochiKit.Base.queryString(
            {'width': dim.w, 'height': dim.h});

        var image_url = window.context_url + '/@@imp-scaled?' + query_string;
        this.image.src = image_url; 
    },

    handle_mouse_wheel: function(event) {
        var zoom = event.mouse().wheel.y;
        this.zoom = this.zoom + this.zoom * zoom / 256
        if (this.zoom <= 0) {
            this.zoom = 0.001;
        }
        log('INFO', 'Zooming ' + zoom+" new zoom " + this.zoom);
        this.zoom_image();
    },

});

MochiKit.Signal.connect(window, 'onload', function() {
    new zeit.imp.Imp();
});
