// Copyright (c) 2008 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.imp = {}

zeit.imp.Imp = Class.extend({

    construct: function() {
        var othis = this;
        this.zoom_grid = 0.0625;

        this.original_dimensions = new MochiKit.DOM.Dimensions(
            new Number($('imp-width').textContent),
            new Number($('imp-height').textContent));
        this.current_dimensions = this.original_dimensions;
        this.mask_dimensions = null;
        this.mask_variable = null;
        this.border = false;

        this.image = null;
        this.loading_image = $('imp-loading-image');
        this.mask_image = $('imp-mask-image')

        this.zoom = (this.get_visual_area_dimensions().w / 
                     this.original_dimensions.w); 

        this.image_dragger = new MochiKit.DragAndDrop.Draggable(
            'imp-image-drag', {
            'handle': $('imp-mask'),
            'starteffect': null,
            'zindex': 0,
        });
        MochiKit.Signal.connect(
            'imp-mask', 'onmousedown',
            this, 'start_drag_change_mouse_cursor');
        MochiKit.Signal.connect(
            'imp-mask', 'onmouseup',
            this, 'end_drag_change_mouse_cursor');
        MochiKit.Signal.connect(
            'imp-mask', 'onmousewheel', this, 'handle_mouse_wheel');
        MochiKit.Signal.connect(
            'imp-configuration', 'onchange', this, 'handle_mask_select');
        MochiKit.Signal.connect(
            'imp-action-crop', 'onclick', this, 'crop_image');
        MochiKit.Signal.connect(
            this, 'configuration-change',
            this, 'load_mask_on_configuration_change');
            

        this.zoom_image();
        var ident = MochiKit.Signal.connect(
            this.image, 'onload', function() {
                //MochiKit.DOM.removeElementClass(othis.image, 'hidden');
                MochiKit.Signal.disconnect(ident);
                othis.ui_loading(false);
        });

    },

    get_visual_area_dimensions: function() {
        return MochiKit.Style.getElementDimensions('imp-image-area');
    },

    get_visual_center: function() {
        if (this.image == null) {
            return new MochiKit.Style.Coordinates(0, 0);
        }
        var dim = this.get_visual_area_dimensions();
        pos = this.get_image_position();
        return new MochiKit.Style.Coordinates(
            Math.floor(dim.w / 2 - pos.x),
            Math.floor(dim.h / 2 - pos.y));
    },

    get_image_position: function() {
        return MochiKit.Style.getElementPosition(
            'imp-image-drag', 'imp-image-area');
    },

    zoom_image: function() {
        var othis = this;

        // First, scale using the browser's scaling capabilities.
        var old_center = this.get_visual_center();

        if (this.image == null) {
            this.image = $('imp-image-drag').appendChild(
                IMG({'id': 'imp-image'}));
        }

        var old_dim = this.current_dimensions;
        var rnd = Math.floor

        var new_dim = new MochiKit.DOM.Dimensions(
            rnd(this.original_dimensions.w * this.zoom),
            rnd(this.original_dimensions.h * this.zoom));
        this.current_dimensions = new_dim;
        MochiKit.Style.setElementDimensions(this.image, new_dim);

        // Move the image so that the center of the visual area stays fixed
        var new_center = new MochiKit.Style.Coordinates(
            rnd(old_center.x * new_dim.w / old_dim.w),
            rnd(old_center.y * new_dim.h / old_dim.h));
        
            var old_pos = this.get_image_position();
            var new_pos = new MochiKit.Style.Coordinates(
                old_pos.x + old_center.x - new_center.x -1,
                old_pos.y + old_center.y - new_center.y -1);
            MochiKit.Style.setElementPosition('imp-image-drag', new_pos);

        log("INFO", 'New pos '+ new_pos.x+'x'+new_pos.y);

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

    crop_image: function() {
        var othis = this;
        if (this.cropping) {
            // Do not run this twice
            return;
        }
        if (!this.mask_dimensions) {
            return;
        }
        this.cropping = true;
        this.ui_loading(true);

        // Calculate crop box
        var image_pos = this.get_image_position();
        var visual_dim = this.get_visual_area_dimensions();
        var f = Math.floor
        var x1 = f(-image_pos.x + visual_dim.w/2 - this.mask_dimensions.w/2);
        var y1 = f(-image_pos.y + visual_dim.h/2 - this.mask_dimensions.h/2);
        var x2 = f(-image_pos.x + visual_dim.w/2 + this.mask_dimensions.w/2);
        var y2 = f(-image_pos.y + visual_dim.h/2 + this.mask_dimensions.h/2);

        // Crop on server
        var crop_url = window.context_url + '/@@imp-crop'
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            crop_url, {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'w': this.current_dimensions.w,
                'h': this.current_dimensions.h,
                'name': this.mask_dimensions.w + 'x' + this.mask_dimensions.h,
                'border': this.border?'1':'',
            });

        d.addCallback(function(result) {
            MochiKit.Signal.signal('content', 'imp-image-cropped')
            othis.cropping = false;
            othis.ui_loading(false);
            });
    },


    handle_mouse_wheel: function(event) {
        var zoom = -event.mouse().wheel.y;
        this.zoom = this.zoom + 1/Math.pow(256, 2) * Math.pow(zoom, 2) * 
            zoom/Math.abs(zoom);
        if (this.zoom <= 0) {
            this.zoom = 0.001;
        }
        log('INFO', 'Zooming ' + zoom+" new zoom " + this.zoom);
        this.zoom_image();
    },

    handle_mask_select: function(event) {
        var target = event.target();
        if (target.name == 'mask') {
            this.parse_mask_string(target.value);
        } else if (target.name == 'border') {
            this.border = target.checked;
        }
        MochiKit.Signal.signal(this, 'configuration-change', {});
    },

    parse_mask_string: function(value) {
        this.mask_variable = {w: false, h: false}
        var mask_width = value.split('x')[0];
        if (mask_width[0] == '?') {
            mask_width = mask_width.substr(1)
            this.mask_variable.w = true;
        }
        var mask_height = value.split('x')[1];
        if (mask_height[0] == '?') {
            mask_height = mask_height .substr(1)
            this.mask_variable.h = true;
        }
        
        this.mask_dimensions = new MochiKit.DOM.Dimensions(
            new Number(mask_width), new Number(mask_height));
    },

    load_mask_on_configuration_change: function(event) {
        var dim = this.get_visual_area_dimensions();
        var mask = this.mask_dimensions;
        if (!mask) {
            return
        }
        var query = MochiKit.Base.queryString({
            'image_width': dim.w,
            'image_height': dim.h,
            'mask_width': mask.w,
            'mask_height': mask.h,
            'border': this.border?'yes':'',
            });
        this.mask_image.setAttribute(
            'src',
            window.application_url + '/@@imp-cut-mask?' + query);
    },

    ui_loading: function(loading) {
        // Indicate loading
        if (loading) {
            MochiKit.DOM.removeElementClass(this.loading_image, 'hidden');
        } else {
            MochiKit.DOM.addElementClass(this.loading_image, 'hidden');
        }
    },

    start_drag_change_mouse_cursor: function(event) {
        MochiKit.DOM.addElementClass('imp-mask', 'dragging');
    },

    end_drag_change_mouse_cursor: function(event) {
        MochiKit.DOM.removeElementClass('imp-mask', 'dragging');
    },

});


zeit.imp.ImageBar = Class.extend({

    construct: function() {
        this.container = $('imp-image-bar');
        this.load();
        MochiKit.Signal.connect(
            'content', 'imp-image-cropped', this, 'load');
    },

    load: function() {
        var othis = this;
        var d = MochiKit.Async.loadJSONDoc(
            window.context_url + '/@@imp-image-bar');
        d.addCallback(function(result) {
            othis.replace_images(result);
        });
    },

    replace_images: function(image_data) {
        var othis = this;
        othis.container.innerHTML = '';
        forEach(image_data, function(image) {
            // Add a query argument because we really cannot cache here.
            var url = (image.url + '/metadata-preview?q=' +
                new Number(new Date()));
            othis.container.appendChild(
                DIV({'class': 'image'},
                    IMG({'src': url}), 
                    SPAN({}, image.name)));
        });
    },

});

MochiKit.Signal.connect(window, 'onload', function() {
    document.imp = new zeit.imp.Imp();
    new zeit.imp.ImageBar();
});
