// IMP

zeit.imp = {}

zeit.imp.Imp = Class.extend({

    construct: function() {
        var othis = this;
        this.zoom = 1;
        this.zoom_grid = 0.0625;

        this.original_dimensions = new MochiKit.DOM.Dimensions(
            new Number($('imp-width').textContent),
            new Number($('imp-height').textContent));

        this.image = $('imp-image');
        this.mask_image = $('imp-mask-image')

        this.image_dragger = new MochiKit.DragAndDrop.Draggable(
            'imp-image-drag', {
            'handle': $('imp-mask'),
            'starteffect': null,
            'zindex': 0,
        });
        MochiKit.Signal.connect(
            'imp-mask', 'onmousewheel', this, 'handle_mouse_wheel');
        MochiKit.Signal.connect(
            'imp-mask-choice', 'onchange', this, 'handle_mask_select');

        this.load_image(this.original_dimensions);
        var ident = MochiKit.Signal.connect(
            this.image, 'onload', function() {
                removeElementClass(othis.image, 'loading');
                MochiKit.Signal.disconnect(ident);
        });

    },

    get_image_dimensions: function() {
        return MochiKit.Style.getElementDimensions('imp-image-area');
    },

    zoom_image: function() {
        var othis = this;

        // First, scale using the browser's scaling capabilities.
        var new_dim = new MochiKit.DOM.Dimensions(
            this.original_dimensions.w * this.zoom,
            this.original_dimensions.h * this.zoom);
        MochiKit.Style.setElementDimensions(this.image, new_dim);

        // Second, scale on server 
        // Fit dim into grid
        var grid_zoom = this.zoom - this.zoom % this.zoom_grid;
        if (grid_zoom < this.zoom) {
            // This is only *not* the case when there was no remainder
            grid_zoom += this.zoom_grid;
        }

        var server_dim = new MochiKit.DOM.Dimensions(
            this.original_dimensions.w * grid_zoom,
            this.original_dimensions.h * grid_zoom);

        if (this._zoom_deferred) {
            this._zoom_deferred.cancel();
        }
        this._zoom_deferred = MochiKit.Async.callLater(
            0.25, function() {othis.load_image(server_dim)});
    },


    load_image: function(dim) {
        log('INFO', "Loading " + dim.w + "x" + dim.h);
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

    handle_mask_select: function(event) {
        var select = event.target();
        if (!select.nodeName == 'INPUT') {
            return
        }
        var dim = this.get_image_dimensions();
        var mask_width = select.value.split('x')[0];
        var mask_height = select.value.split('x')[1];
        var query = MochiKit.Base.queryString({
            'image_width:int': dim.w,
            'image_height:int': dim.h,
            'mask_width:int': mask_width,
            'mask_height:int': mask_height});
        this.mask_image.src = window.application_url + '/@@imp-cut-mask?' +
            query;
    },

});

MochiKit.Signal.connect(window, 'onload', function() {
    new zeit.imp.Imp();
});
