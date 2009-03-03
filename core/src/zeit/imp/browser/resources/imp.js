// Copyright (c) 2008-2009 gocept gmbh & co. kg
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
        this.mask_image_dimensions = null;
        this.mask_variable = null;
        this.border = MochiKit.Iter.ifilter(
            function(elem) { return elem.checked },
            $('imp-configuration-form')['border']).next().value;
        // Point for extensions to add arguments.
        this.crop_arguments = {}

        this.image = null;
        this.image_server_dimensions = null;
        this.loading_image = $('imp-loading-image');
        this.mask_image = null;

        this.zoom = (this.get_visual_area_dimensions().w / 
                     this.original_dimensions.w); 
        this.stored_visual_area_dimensions = this.get_visual_area_dimensions();
        this.image_dragger = new MochiKit.DragAndDrop.Draggable(
            'imp-image-drag', {
            'handle': $('imp-mask'),
            'starteffect': null,
            'zindex': 0,
        });
        
        this.resize_monitor = new zeit.imp.ResizeMonitor('imp-image-area');
        MochiKit.Signal.connect(
            this.resize_monitor, 'resize', function(event) {
                MochiKit.Signal.signal(othis, 'resize');
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
        MochiKit.Signal.connect(
            this, 'configuration-change',
            function() {
                if (!MochiKit.Base.isNull(othis.image_server_dimensions)) {
                    othis.load_image(othis.image_server_dimensions)
                }
            });

        MochiKit.Signal.connect(
            this, 'resize', this, 'load_mask_on_configuration_change');
        MochiKit.Signal.connect(
            this, 'resize', this, 'move_image_on_size_change');


        this.zoom_image();
        var ident = MochiKit.Signal.connect(
            this.image, 'onload', function() {
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
        MochiKit.Signal.signal(this, 'zoom-change');
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

        this.image_server_dimensions = new MochiKit.DOM.Dimensions(
            Math.floor(this.original_dimensions.w * grid_zoom),
            Math.floor(this.original_dimensions.h * grid_zoom));

        if (this._zoom_deferred) {
            this._zoom_deferred.cancel();
        }
        this._zoom_deferred = MochiKit.Async.callLater(
            0.25, function() {
                othis.load_image(othis.image_server_dimensions)});
    },


    load_image: function(dim) {
        log('INFO', "Loading " + dim.w + "x" + dim.h);
        var query = {'width': dim.w, 'height': dim.h};
        MochiKit.Base.update(query, this.crop_arguments);
        var query_string = MochiKit.Base.queryString(query);
        var image_url = window.context_url + '/@@imp-scaled?' + query_string;
        this.image.src = image_url; 
    },

    get_crop_arguments: function() {
        if (!this.mask_dimensions) {
            return null;
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
        var args = MochiKit.Base.clone(this.crop_arguments);
        MochiKit.Base.update(args, 
            {'x1': x1,
             'y1': y1,
             'x2': x2,
             'y2': y2,
             'w': this.current_dimensions.w,
             'h': this.current_dimensions.h,
             'name': this.name,
             'border': this.border});
        return args;
    },

    crop_image: function() {
        var othis = this;
        if (this.cropping) {
            // Do not run this twice
            return;
        }
        var crop_arguments = this.get_crop_arguments();
        if (crop_arguments === null) {
            return;
        } 

        // Crop on server
        var crop_url = window.context_url + '/@@imp-crop'
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            crop_url, crop_arguments);
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
            this.border = target.value;
        } else {
            return
        }
        MochiKit.Signal.signal(this, 'configuration-change', {});
    },

    parse_mask_string: function(value) {
        this.name = value.split('/')[0]
        this.mask_variable = {w: false, h: false}
        var mask_width = value.split('/')[1];
        if (mask_width[0] == '?') {
            mask_width = mask_width.substr(1)
            this.mask_variable.w = true;
        }
        var mask_height = value.split('/')[2];
        if (mask_height[0] == '?') {
            mask_height = mask_height .substr(1)
            this.mask_variable.h = true;
        }
        
        this.mask_dimensions = new MochiKit.DOM.Dimensions(
            new Number(mask_width), new Number(mask_height));
    },

    load_mask_on_configuration_change: function(event) {
        var mask = this.mask_dimensions;
        if (!mask) {
            return
        }
        this.mask_image_dimensions = this.get_visual_area_dimensions();
        var query = MochiKit.Base.queryString({
            'image_width': this.mask_image_dimensions.w,
            'image_height': this.mask_image_dimensions.h,
            'mask_width': mask.w,
            'mask_height': mask.h,
            'border': this.border,
            });
        var image_url = window.application_url + '/@@imp-cut-mask?' + query;
        if (this.mask_image === null) {
            this.mask_image = $('imp-mask').appendChild(
                IMG({'id': 'imp-mask-image', 'src': image_url}))
        } else {
            this.mask_image.setAttribute('src', image_url);
        }
    },

    move_image_on_size_change: function(event) {
        var pos = this.get_image_position();
        pos.x -= 1;
        pos.y -= 1;
        log('INFO', pos.__repr__());

        var dim = this.get_visual_area_dimensions();
        var move_x = Math.floor((
            this.stored_visual_area_dimensions.w - dim.w) / 2);
        var move_y = Math.floor((
            this.stored_visual_area_dimensions.h - dim.h) / 2);
        pos.x -= move_x;
        pos.y -= move_y;
        MochiKit.Style.setElementPosition('imp-image-drag', pos);
        this.stored_visual_area_dimensions = dim;
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


zeit.imp.ImageData = Class.extend({

    construct: function() {
        this.container = $('imp-image-bar');
        this.data = null;
        this.load();
        MochiKit.Signal.connect(
            'content', 'imp-image-cropped', this, 'load');
    },

    load: function() {
        var othis = this;
        var d = MochiKit.Async.loadJSONDoc(
            window.context_url + '/@@imp-image-bar');
        d.addCallback(function(result) {
            othis.data = result;
            MochiKit.Signal.signal(othis, 'data-changed', result);
        });
    },


});


zeit.imp.ImageBar = Class.extend({

    construct: function() {
        this.container = $('imp-image-bar');
        MochiKit.Signal.connect(
            document.imp_data, 'data-changed', this, 'replace_images');
    },

    replace_images: function(image_data) {
        var othis = this;
        othis.container.innerHTML = '';
        var divs = [];
        forEach(image_data, function(image) {
            // Add a query argument because we really cannot cache here.
            var url = (image.url + '/metadata-preview?q=' +
                new Number(new Date()));
            divs.push(
                DIV({'class': 'image'},
                    IMG({'src': url}), 
                    SPAN({}, image.name)));
        });
        if (divs.length > 0) {
            othis.container.appendChild(DIV({}, divs));
        }
    },

});


zeit.imp.ZoomSlider = Class.extend({

    construct: function(imp) {
        this.imp = imp;
        this.zoom_slider = null;
        this.init();
        MochiKit.Signal.connect(this.imp, 'resize', this, 'init');
        MochiKit.Signal.connect(
            this.imp, 'zoom-change', this, 'update_slider_from_zoom');
    },

    init: function() {
        if (this.zoom_slider !== null) {
            MochiKit.Signal.disconnectAll(this.zoom_slider);
        }
        this.zoom_slider = new UI.Slider(
            'imp-zoom-slider', 3001,
            UI.Slider.ValueMappers.range(0, 3, 0.001));
        this.zoom_slider.setValue(this.imp.zoom);
        MochiKit.Signal.connect(
            this.zoom_slider, 'valueChanged',
            this, 'update_zoom_from_slider');
    },

    update_zoom_from_slider: function(event) {
        this.imp.zoom = this.zoom_slider.value;
        this.imp.zoom_image();
    },

    update_slider_from_zoom: function(event) {
        this.zoom_slider.setValue(this.imp.zoom);
    },

    get_value: function() {
        return this.zoom_slider.value;
    },

});


zeit.imp.DynamicMask = Class.extend({

    construct: function(imp) {
        this.imp = imp;
        var form = $('imp-configuration-form')
        this.input_w = form['mask-w'];
        this.input_h = form['mask-h'];
        this.d_value_change = null;
        MochiKit.Signal.connect(
            this.imp, 'configuration-change', this, 'update_inputs');
        this.connect_inputs('onkeydown', 'handle_input_keydown');
        this.connect_inputs('onkeyup', 'handle_input_keyup');
        this.connect_inputs('onchange', 'handle_input_change');
    },

    connect_inputs: function(event, method_name) {
        MochiKit.Signal.connect(this.input_w, event, this, method_name)
        MochiKit.Signal.connect(this.input_h, event, this, method_name)
    },

    update_inputs: function(event) {
        var dim = this.imp.mask_dimensions;
        if (dim === null) {
            return
        }
        this.input_w.value = dim.w;
        this.input_h.value = dim.h;
        this.set_disabled(this.input_w, !this.imp.mask_variable.w);
        this.set_disabled(this.input_h, !this.imp.mask_variable.h);
    },

    set_disabled: function(input, value) {
        input.disabled = value;
        if (value) {
            input.setAttribute('disabled', 'disabled');
        }
    },

    update_mask: function() {
        this.imp.mask_dimensions.w = new Number(this.input_w.value);
        this.imp.mask_dimensions.h = new Number(this.input_h.value);
        MochiKit.Signal.signal(this.imp, 'configuration-change');
    },

    handle_input_keydown: function(event) {
        var othis = this;
        var input = event.target();
        var key = event.key()['string'];
        if (key == 'KEY_ARROW_UP' || key == 'KEY_ARROW_RIGHT') {
            var delta = 1;
        } else if (key == 'KEY_ARROW_DOWN' || key == 'KEY_ARROW_LEFT') {
            var delta = -1;
        } else {
            return
        }
        event.stop();
        var delay = 0.25;
        var value_changer = function() {
            input.value = new Number(input.value) + delta;
            othis.d_value_change = MochiKit.Async.callLater(
                delay, value_changer);
            delay = 0.05
        };
        value_changer();
    },

    handle_input_keyup: function(event) {
        if (this.d_value_change == null) {
            return
        }
        this.d_value_change.cancel()
        this.d_value_change = null;
        this.update_mask();
    },

    handle_input_change: function(event) {
        this.update_mask();
    },

});


zeit.imp.AlreadyCroppedIndicator = Class.extend({

    construct: function() {
        MochiKit.Signal.connect(
            document.imp_data, 'data-changed', this, 'update');
    },
    
    update: function(image_data) {
        var othis = this;
        var names = {};
        forEach(image_data, function(image) {
            names[image.scale_name] = true;
        });

        forEach($('imp-configuration-form')['mask'], function(mask) {
            var func;
            var name = mask.value.split('/')[0];
            var label = mask.parentNode;
            if (name in names) {
                func = MochiKit.DOM.addElementClass;
            } else {
                func = MochiKit.DOM.removeElementClass;
            }
            func(label, 'cropped');
        });
    },

});


zeit.imp.ResizeMonitor = Class.extend({

    construct: function(monitor_element) {
        var othis = this;
        this.element = $(monitor_element);
        this.dimensions = this.get_current_dimensions();
        var check = function() {
            var new_dimensions = othis.get_current_dimensions();
            if (!(new_dimensions.w == othis.dimensions.w &&
                new_dimensions.h == othis.dimensions.h)) {
                othis.dimensions = new_dimensions;
                MochiKit.Signal.signal(othis, 'resize');
            }
            MochiKit.Async.callLater(0.25, check);
        };
        check();
    },

    get_current_dimensions: function() {
        return MochiKit.Style.getElementDimensions(this.element);
    },
});


zeit.imp.ImageFilter = Class.extend({

    construct: function(name) {
        this.name = name;
        this.container = $('filter.' + this.name);
        var input_id = 'filter.' + name + '.input';
        this.input_element = this.container.appendChild(
            INPUT({'type': 'text',
                   'name': 'filter.' + this.name,
                   'id': input_id,
                   'value': '1',
                   'class': 'filter'}));
        this.slider_element = this.container.appendChild(
            DIV({'class': 'uislider'}))
        MochiKit.DOM.getFirstElementByTagAndClassName(
            'label', null, this.container).setAttribute('for', input_id);

        this.slider = new UI.Slider(
            this.slider_element, 2001,
            [this.to_value, this.to_step],
            this.input_element);
        this.reset();

        MochiKit.Signal.connect(
            this.slider, 'valueChanged', this, 'update_crop_arguments');
        this.signal_deferred = null;
        MochiKit.Signal.connect(
            'imp-action-reset', 'onclick', this, 'reset');
    },

    reset: function() {
        this.slider.setValue(0);
    },

    update_crop_arguments: function(event) {
        var self = this;
        document.imp.crop_arguments['filter.' + self.name] = self.to_filter(
            self.slider.value);
        if (!MochiKit.Base.isNull(self.signal_deferred)) {
            self.signal_deferred.cancel();
        }
        self.signal_deferred = MochiKit.Async.callLater(
            0.25, function() {
                MochiKit.Signal.signal(document.imp, 'configuration-change');
                self.signal_deferred = null;
            });
    },

    to_value: function(step) {
        // [0; 2000] --> [-100; 100]
        return new Number((step / 10 - 100).toPrecision(3));
    },

    to_step: function(value) {
        // [-100; 100] --> [0; 2000]
        return (value + 100) * 10;
    },

    to_filter: function(value) {
        if (value < 0) {
            // scale to [0;1]
            return (value + 100) / 100;
        } else {
            // scale to ]1;11]
            return value / 10 + 1;
        }
    },

});


MochiKit.Signal.connect(window, 'onload', function() {
    document.imp = new zeit.imp.Imp();
    document.imp_zoom_slider = new zeit.imp.ZoomSlider(document.imp);
    document.imp_data = new zeit.imp.ImageData();
    new zeit.imp.DynamicMask(document.imp);
    new zeit.imp.ImageBar();
    new zeit.imp.AlreadyCroppedIndicator();
    // Filters
    new zeit.imp.ImageFilter('brightness');
    new zeit.imp.ImageFilter('contrast');
    new zeit.imp.ImageFilter('sharpness');
    document.imp_color_filter = new zeit.imp.ImageFilter('color');
});
