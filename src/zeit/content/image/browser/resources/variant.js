/*global zeit,Backbone,window,document*/
(function() {
    "use strict";

    var $ = window.jQuery;
    var _ = window.Underscore;

    zeit.cms.declare_namespace('zeit.content.image');
    zeit.cms.declare_namespace('zeit.content.image.browser');


    /* ===================================================================== */
    /* ============================= MODELS ================================ */
    /* ===================================================================== */

    zeit.content.image.Variant = Backbone.Model.extend({
        urlRoot: window.context_url + '/variants',

        image_enhancement: function(name, new_value) {
            var self = this,
                old_value = self.get(name);

            if (new_value !== undefined) {
                if (!isNaN(new_value)) {
                    self.set(name, new_value / 200 + 1);
                    return true;
                }
                return false;
            }

            if (old_value === null) {
                return 0;
            }
            return Math.round((old_value - 1) * 200);
        },

        brightness: function(value) {
            return this.image_enhancement('brightness', value);
        },

        contrast: function(value) {
            return this.image_enhancement('contrast', value);
        },

        saturation: function(value) {
            return this.image_enhancement('saturation', value);
        },

        sharpness: function(value) {
            return this.image_enhancement('sharpness', value);
        },

        make_url: function() {
            var self = this,
                url = self.escape('url');
            return url + '?nocache=' + new Date().getTime();
        },

        /* Calculate FP and Zoom from offeset and dimension of Cropping UI. */
        update_from_rectangle: function(cropbox, image) {
            var self = this,
                zoom,
                focus_x,
                focus_y,
                image_width = image.naturalWidth,
                image_height = image.naturalHeight;

            zoom = Math.max(
                cropbox.width / image_width,
                cropbox.height / image_height
            );

            // rectangle uses full width, i.e. it does not matter where the
            // focus point is; use 1/2 as default since calculation would fail
            // (also check > due to rounding issues of js.cropper)
            if (cropbox.width >= image_width) {
                focus_x = 1 / 2;
            } else {
                focus_x = cropbox.x / (image_width - cropbox.width);
            }

            // rectangle uses full height, i.e. it does not matter where the
            // focus point is; use 1/3 as default since calculation would fail
            // (also check > due to rounding issues of js.cropper)
            if (cropbox.height >= image_height) {
                focus_y = 1 / 3;
            } else {
                focus_y = cropbox.y / (image_height - cropbox.height);
            }

            // guard against rounding issues
            if (zoom > 1) { zoom = 1; }
            if (focus_x > 1) { focus_x = 1; }
            if (focus_y > 1) { focus_y = 1; }

            return self.save(
                {"focus_x": focus_x, "focus_y": focus_y, "zoom": zoom}
            );
        },

        /* Calculate offset and dimension of Cropping UI using FP and Zoom. */
        calc_rectangle_placement: function(image) {
            var self = this,
                offset_x,
                offset_y,
                width,
                height,
                image_width = image.naturalWidth,
                image_height = image.naturalHeight,
                image_ratio = image_width / image_height;

            // adjust width / height according to their ratio,
            // e.g. square has ratio 1, thus width = height
            if (self.get('ratio') > image_ratio) {
                height = image_width / self.get('ratio');
                width = image_width;
            } else {
                width = image_height * self.get('ratio');
                height = image_height;
            }

            // incorporate zoom to have final width / height of rectangle
            height = height * self.get('zoom');
            width = width * self.get('zoom');

            offset_x = self.get('focus_x') * (image_width - width);
            offset_y = self.get('focus_y') * (image_height - height);

            return {
                x: offset_x,
                y: offset_y,
                width: width,
                height: height,
                rotate: 0
            };
        }
    });


    zeit.content.image.VariantList = Backbone.Collection.extend({

        model: zeit.content.image.Variant,
        url: window.context_url + '/variants',

        // Copy onModelEvent from Backbone and remove the removal of models,
        // since when we send DELETE model to server, we just mean to reset it,
        // i.e. we still need to keep it to update the preview image
        _onModelEvent: function(event, model, collection, options) {
            if ((event === 'add' || event === 'remove') && collection !== this) return;
            // if (event === 'destroy') this.remove(model, options);
            if (model && event === 'change:' + model.idAttribute) {
                delete this._byId[model.previous(model.idAttribute)];
                if (model.id != null) this._byId[model.id] = model;
            }
            this.trigger.apply(this, arguments);
        }

    });


    zeit.content.image.VARIANTS = new zeit.content.image.VariantList();


    /* ===================================================================== */
    /* ============================== VIEWS ================================ */
    /* ===================================================================== */

    var AbstractVariant = Backbone.View.extend({

        create_image: function() {
            var self = this,
                image = $('<img/>');

            // Event handler so Jasmine tests can wait for the image to load.
            image.on('load', function() {
                self.trigger('render');
            });

            // Set src attribute after event registration
            image.attr('src', self.model.make_url());

            return image;
        }
    });

    /* PreviewVariant is used by VariantList only. */
    zeit.content.image.browser.PreviewVariant = AbstractVariant.extend({

        render: function() {
            var self = this,
                name,
                image = self.create_image();

            if (self.model.has('display_name')) {
                name = self.model.escape('display_name');
            } else {
                name = self.model.escape('id');
            }

            self.$el.addClass('preview-container');
            self.$el.append(
                $('<span class="preview-title">' + name + '</span>')
            );
            self.$el.append(image);

            return self;
        },

        create_image: function() {
            var self = this,
                image = AbstractVariant.prototype.create_image.apply(this);

            image.addClass('preview');

            // Set max-width defined in config as width to display smaller
            // sizes of a variant as big as allowed.
            if (self.model.has('max_size')) {
                var size = self.model.escape('max_size').split('x');
                image.width(size[0]);
            }

            // Notify world that image was clicked to make the model active.
            image.on('click', function() {
                self.model.trigger('switch-focus', self.model, self);
            });

            return image;
        },

        update_image: function() {
            this.$('img').attr('src', this.model.make_url());
        }
    });


    /* EditableVariant is used by VariantEditor only. */
    zeit.content.image.browser.EditableVariant = AbstractVariant.extend({

        render: function() {
            var self = this,
                image = self.create_image();

            // Replace default DIV element with img and rewire events.
            self.$el.replaceWith(image);
            self.setElement(image);

            return self;
        },

        create_image: function() {
            var self = this,
                image = AbstractVariant.prototype.create_image.apply(this);

            image.addClass('editor');

            return image;
        },

        update_image: function() {
            this.$el.attr('src', this.model.make_url());
        }
    });


    zeit.content.image.browser.VariantList = Backbone.View.extend({

        el: '#variant-preview',

        initialize: function() {
            this.listenTo(zeit.content.image.VARIANTS, 'reset', this.reset);
            this.listenTo(zeit.content.image.VARIANTS, 'reload', this.reload);
            this.model_views = {};
        },

        reset: function() {
            // Render all models. Used for initial load.
            var self = this;
            self.$el.empty();
            zeit.content.image.VARIANTS.each(function(variant) {
                var view = new zeit.content.image.browser.PreviewVariant(
                    {model: variant}
                );
                self.model_views[variant.id] = view;
                self.$el.append(view.render().el);
            });
        },

        reload: function(variant_view) {
            // Only update src attribute of images to reload them.
            var self = this;

            // Update the variant that was changed, unless it's the default one
            if (!variant_view.model.get('is_default')) {
                variant_view.update_image();
                return;
            }

            // Update master image and all previews
            variant_view.update_image();
            $.each(self.model_views, function(id, view) {
                view.update_image();
            });
        }

    });


    zeit.content.image.browser.VariantEditor = Backbone.View.extend({

        el: '#variant-inner',

        events: {
            "built.cropper img.editor": "update",
            "dragend.cropper img.editor": "save",
            "dragstop .focuspoint": "save",
            "slidestop .zoom-bar": "save",
            "slidestop .image-enhancement-bar": "save_image_enhancement",
            "blur .image-enhancement-input": "save_image_enhancement"
        },

        initialize: function() {
            var self = this;
            self.default_model = new zeit.content.image.Variant(
                {id: 'default'}
            );
            self.current_model = self.default_model;
            self.model_view = new zeit.content.image.browser.EditableVariant(
                {model: self.current_model}
            );

            self.model_view.on('render', function() {
                self.trigger('render');
            });

            self.listenTo(
                zeit.content.image.VARIANTS,
                'switch-focus',
                self.switch_focus
            );
        },

        prepare: function () {
            var self = this;
            self.default_model.fetch().done(function() {
                self.render();
            });
        },

        render: function() {
            var self = this;
            self.image = self.model_view.render().$el;

            // create DOM to display the image and image controls
            self.$el.append(
                $('<div class="image-container"></div>').append(
                    $('<div class="focuspoint"></div>').append(
                        $('<div class="circle"></div>')
                    )
                ).append(self.image).add('<div class="zoom-bar"></div>')
            );

            // create DOM for all buttons
            self.reset_all_button = $(
                '<input type="submit" class="button" '
                    + 'value="Alle Formate zurücksetzen" />');
            self.reset_current_button = $(
                '<input type="submit" class="button" value="Verwerfen" />');
            self.save_current_button = $(
                '<input type="submit" class="button" value="Speichern" />');

            // add buttons to DOM node
            self.$el.append([
                self.reset_all_button,
                self.reset_current_button,
                self.save_current_button
            ]);

            // bind DOM elements to variables for later use
            self.focuspoint = self.$('.focuspoint');
            self.zoom_bar = self.$('.zoom-bar');

            // create input elements for image enhancement
            var blur_on_enter = function (event) {
                if (event.which === 13) {
                    event.target.blur();
                }
            };

            // Brightness
            self.$el.append($('\
                <div class="widget filter" id="filter.brightness">\
                    <label for="filter.brightness.input">\
                        Helligkeit\
                    </label>\
                    <input type="text" name="filter.brightness" class="brightness-input image-enhancement-input" value="1" class="filter">\
                    <div class="image-enhancement-bar brightness-bar"></div>\
                </div>'));

            self.brightness_input = self.$('.brightness-input');
            self.brightness_input.on('keydown', blur_on_enter);
            self.brightness_input.val(self.current_model.brightness());
            self.brightness_bar = self.$('.brightness-bar');
            self.brightness_bar.slider({
                step: 1,
                min: -100,
                max: 100,
                value: self.current_model.brightness()
            });

            // Contrast
            self.$el.append($('\
                <div class="widget filter" id="filter.contrast">\
                    <label for="filter.contrast.input">\
                        Kontrast\
                    </label>\
                    <input type="text" name="filter.contrast" class="contrast-input image-enhancement-input" value="1" class="filter">\
                    <div class="image-enhancement-bar contrast-bar"></div>\
                </div>'));

            self.contrast_input = self.$('.contrast-input');
            self.contrast_input.on('keydown', blur_on_enter);
            self.contrast_input.val(self.current_model.contrast());
            self.contrast_bar = self.$('.contrast-bar');
            self.contrast_bar.slider({
                step: 1,
                min: -100,
                max: 100,
                value: self.current_model.contrast()
            });

            // saturation
            self.$el.append($('\
                <div class="widget filter" id="filter.saturation">\
                    <label for="filter.saturation.input">\
                        Sättigung\
                    </label>\
                    <input type="text" name="filter.saturation" class="saturation-input image-enhancement-input" value="1" class="filter">\
                    <div class="image-enhancement-bar saturation-bar"></div>\
                </div>'));

            self.saturation_input = self.$('.saturation-input');
            self.saturation_input.on('keydown', blur_on_enter);
            self.saturation_input.val(self.current_model.saturation());
            self.saturation_bar = self.$('.saturation-bar');
            self.saturation_bar.slider({
                step: 1,
                min: -100,
                max: 100,
                value: self.current_model.saturation()
            });

            // sharpness
            self.$el.append($('\
                <div class="widget filter" id="filter.sharpness">\
                    <label for="filter.sharpness.input">\
                        Schärfe\
                    </label>\
                    <input type="text" name="filter.sharpness" class="sharpness-input image-enhancement-input" value="1" class="filter">\
                    <div class="image-enhancement-bar sharpness-bar"></div>\
                </div>'));

            self.sharpness_input = self.$('.sharpness-input');
            self.sharpness_input.on('keydown', blur_on_enter);
            self.sharpness_input.val(self.current_model.sharpness());
            self.sharpness_bar = self.$('.sharpness-bar');
            self.sharpness_bar.slider({
                step: 1,
                min: -100,
                max: 100,
                value: self.current_model.sharpness()
            });

            // init draggging / zooming
            self.initialize_focuspoint();
            self.initialize_buttons();

            // set focuspoint and zoom to saved values
            self.update();
        },

        // Use recursive method to reset all variant configs, since parallel
        // DELETE requests can interfere, thus ending in a `last DELETE wins`
        // scenario. (This is caused by the server, since we replace the
        // variants dict there rather modifying it due to security issues.)
        reset_all_variants: function(variants) {
            var self = this, variant;
            // after all DELETE calls were processed by the server we need to
            // update all images
            if (variants.length == 0) {
                zeit.content.image.VARIANTS.trigger(
                    'reload', self.model_view);
                self.notify_status("reset_all");
                return;
            }

            // let the server process the first variant of the array
            // completely, before processing the next by calling this method
            // recursively
            variant = variants.shift();
            variant.destroy({wait: true}).done(function() {
                self.reset_all_variants(variants);
            });
        },

        initialize_buttons: function() {
            var self = this;

            // hide buttons for editing a single format on startup
            self.reset_current_button.hide();
            self.save_current_button.hide();

            self.reset_all_button.on('click', function() {
                self.reset_all_variants(zeit.content.image.VARIANTS.clone());
            });

            self.reset_current_button.on('click', function() {
                self.current_model.destroy({wait: true}).done(function() {
                    zeit.content.image.VARIANTS.trigger(
                        'reload', self.model_view);
                });
                self.notify_status("reset_single");
                self.switch_focus(
                    self.default_model,
                    new zeit.content.image.browser.EditableVariant(
                        {model: self.default_model}
                    )
                );
            });

            self.save_current_button.on('click', function() {
                self.switch_focus(
                    self.default_model,
                    new zeit.content.image.browser.EditableVariant(
                        {model: self.default_model}
                    )
                );
            });
        },

        initialize_focuspoint: function() {
            var self = this;
            self.focuspoint.draggable({
                containment: self.$('.image-container')
            });

            self.zoom_bar.slider({
                step: 5,
                min: 0,
                max: 75,
                value: 100 - self.current_model.get('zoom') * 100,
                orientation: 'vertical'
            });
        },

        initialize_rectangle: function() {
            var self = this;
            self.image.cropper({
                aspectRatio: self.current_model.get('ratio'),
                zoomable: false,
                autoCrop: false,
                rotatable: false,
                movable: false,
                doubleClickToggle: false
            });
        },

        save_image_enhancement: function () {
            var self = this,
                brightness = self.current_model.brightness(),
                contrast = self.current_model.contrast(),
                saturation = self.current_model.saturation(),
                sharpness = self.current_model.sharpness();

            // Brightness
            if (self.brightness_bar.slider("value") !== self.current_model.brightness()) {
                self.current_model.brightness(self.brightness_bar.slider("value"));
            } else if (parseInt(self.brightness_input.val()) !== self.current_model.brightness()) {
                self.current_model.brightness(parseInt(self.brightness_input.val()));
            }

            if (brightness !== self.current_model.brightness()) {
                self.save();
            }

            // Contrast
            if (self.contrast_bar.slider("value") !== self.current_model.contrast()) {
                self.current_model.contrast(self.contrast_bar.slider("value"));
            } else if (parseInt(self.contrast_input.val()) !== self.current_model.contrast()) {
                self.current_model.contrast(parseInt(self.contrast_input.val()));
            }

            if (contrast !== self.current_model.contrast()) {
                self.save();
            }

            // Saturation
            if (self.saturation_bar.slider("value") !== self.current_model.saturation()) {
                self.current_model.saturation(self.saturation_bar.slider("value"));
            } else if (parseInt(self.saturation_input.val()) !== self.current_model.saturation()) {
                self.current_model.saturation(parseInt(self.saturation_input.val()));
            }

            if (saturation !== self.current_model.saturation()) {
                self.save();
            }

            // Sharpness
            if (self.sharpness_bar.slider("value") !== self.current_model.sharpness()) {
                self.current_model.sharpness(self.sharpness_bar.slider("value"));
            } else if (parseInt(self.sharpness_input.val()) !== self.current_model.sharpness()) {
                self.current_model.sharpness(parseInt(self.sharpness_input.val()));
            }

            if (sharpness !== self.current_model.sharpness()) {
                self.save();
            }
        },

        save: function() {
            var self = this,
                promise;

            if (self.current_model.get('is_default')) {
                promise = self.save_using_focuspoint();
            } else {
                promise = self.save_using_rectangle();
            }

            promise.done(function() {
                self.update();
                zeit.content.image.VARIANTS.trigger(
                    'reload', self.model_view
                );
                self.notify_status("saved");
            });
        },

        save_using_focuspoint: function() {
            var self = this,
                focus_x = self.focuspoint.position().left / self.image.width(),
                focus_y = self.focuspoint.position().top / self.image.height(),
                zoom = (100 - self.zoom_bar.slider("value")) / 100;

            return self.current_model.save(
                {"focus_x": focus_x, "focus_y": focus_y, "zoom": zoom}
            );
        },

        save_using_rectangle: function() {
            var self = this;
            return self.current_model.update_from_rectangle(
                self.image.cropper('getData'),
                self.image.cropper('getImageData')
            );
        },

        update: function() {
            var self = this;

            self.brightness_bar.slider("value", self.current_model.brightness());
            self.brightness_input.val(self.current_model.brightness());

            self.contrast_bar.slider("value", self.current_model.contrast());
            self.contrast_input.val(self.current_model.contrast());

            self.saturation_bar.slider("value", self.current_model.saturation());
            self.saturation_input.val(self.current_model.saturation());

            self.sharpness_bar.slider("value", self.current_model.sharpness());
            self.sharpness_input.val(self.current_model.sharpness());

            if (self.current_model.get('is_default')) {
                self.update_focuspoint();
            } else {
                self.update_rectangle();
            }
        },

        update_focuspoint: function() {
            var self = this;
            self.focuspoint.css(
                'top',
                self.current_model.get('focus_y') * 100 + '%'
            );
            self.focuspoint.css(
                'left',
                self.current_model.get('focus_x') * 100 + '%'
            );
            self.zoom_bar.slider(
                "value",
                100 - self.current_model.get('zoom') * 100
            );
        },

        update_rectangle: function() {
            var self = this;
            self.image.cropper('crop');

            self.image.cropper(
                'setAspectRatio',
                self.current_model.get('ratio')
            );

            self.image.cropper(
                'setData',
                self.current_model.calc_rectangle_placement(
                    self.image.cropper('getImageData')
                )
            );
        },

        switch_focus: function(model, view) {
            var self = this;
            self.image.cropper('destroy');  // no-op if it doesn't exist
            if (!model.get('is_default')) {
                self.zoom_bar.hide();
                self.focuspoint.hide();
                self.reset_all_button.hide();

                self.reset_current_button.show();
                self.save_current_button.show();

                self.initialize_rectangle();
            } else {
                self.zoom_bar.show();
                self.focuspoint.show();
                self.reset_all_button.show();

                self.reset_current_button.hide();
                self.save_current_button.hide();
            }

            self.model_view.$el.removeClass('active');
            self.model_view = view;
            self.model_view.$el.addClass('active');
            self.current_model = model;
            self.current_model.fetch().done(function() {
                self.update();
                self.notify_status("switched");
            });
        },

        notify_status: function(status) {
            // Used for Selenium tests, add `status` as class to element for 2s
            var self = this;
            self.$el.addClass(status);
            window.setTimeout(function () {
                self.$el.removeClass(status);
            }, 2000);
        }
    });


    $(document).ready(function() {
        if (!$('#variant-content').length) {
            return;
        }

        var view = new zeit.content.image.browser.VariantEditor();
        view.prepare();

        new zeit.content.image.browser.VariantList();
        zeit.content.image.VARIANTS.fetch({reset: true});
    });

})();
