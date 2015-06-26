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

        make_url: function() {
            var self = this,
                url = self.escape('url');
            return url + '?nocache=' + new Date().getTime();
        },

        /* Calculate FP and Zoom from offeset and dimension of Cropping UI. */
        update_from_cropper: function(cropbox, image) {
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
        calc_cropper_placement: function(image) {
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
        url: window.context_url + '/variants'

    });


    zeit.content.image.VARIANTS = new zeit.content.image.VariantList();


    /* ===================================================================== */
    /* ============================== VIEWS ================================ */
    /* ===================================================================== */

    var AbstractVariant = Backbone.View.extend({

        render: function() {
            var self = this;
            self.image = self.create_image();

            // Replace default DIV element with img as rewire events.
            self.$el.replaceWith(self.image);
            self.setElement(self.image);

            return self;
        },

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
            this.$el.attr('src', this.model.make_url());
        }
    });


    /* EditableVariant is used by VariantEditor only. */
    zeit.content.image.browser.EditableVariant = AbstractVariant.extend({

        create_image: function() {
            var self = this,
                image = AbstractVariant.prototype.create_image.apply(this);

            image.addClass('editor');

            image.cropper({
                aspectRatio: self.model.get('ratio'),
                zoomable: false,
                autoCrop: false,
                rotatable: false,
                movable: false,
                doubleClickToggle: false
            });

            return image;
        }
    });


    zeit.content.image.browser.VariantList = Backbone.View.extend({

        el: '#variant-preview',

        initialize: function() {
            this.listenTo(zeit.content.image.VARIANTS, 'reset', this.reset);
            this.listenTo(zeit.content.image.VARIANTS, 'reload', this.reload);
            this.model_views = [];
        },

        reset: function() {
            // Render all models. Used for initial load.
            var self = this;
            self.$el.empty();
            zeit.content.image.VARIANTS.each(function(variant) {
                var view = new zeit.content.image.browser.PreviewVariant(
                    {model: variant}
                );
                self.model_views.push(view);
                self.$el.append(view.render().el);
            });
        },

        reload: function() {
            // Only update src attribute of images.
            var self = this;
            $(self.model_views).each(function(index, view) {
                view.update_image();
            });
        }

    });


    zeit.content.image.browser.VariantEditor = Backbone.View.extend({

        el: '#variant-inner',

        events: {
            "dragstop .focuspoint": "save"
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
            self.model_view.img_css_class = 'editor';

            self.model_view.on('render', function() {
                self.trigger('render');
            });

            self.listenTo(zeit.content.image.VARIANTS, 'switch-focus', self.switch_focus);

            $('#reset').on('click', function() {
                self.switch_focus(
                    self.default_model,
                    new zeit.content.image.browser.EditableVariant(
                        {model: self.default_model}
                    )
                );
            });
        },

        prepare: function () {
            var self = this;
            self.default_model.fetch().done(function() {
                self.render();
            });
        },

        render: function() {
            var self = this;

            self.$el.append(self.model_view.render().el);

            self.image = self.$('img');
            self.image.on('built.cropper', function() {
                self.update();
            });
            self.image.on('dragend.cropper', function() {
                self.save();
            });
        },

        save: function() {
            var self = this;

            self.current_model.update_from_cropper(
                self.image.cropper('getData'),
                self.image.cropper('getImageData')
            ).done(function() {
                self.update();
                zeit.content.image.VARIANTS.trigger('reload');
                self.notify_status("saved");
            });
        },

        update: function() {
            var self = this;

            self.image.cropper('crop');

            self.image.cropper(
                'setAspectRatio',
                self.current_model.get('ratio')
            );

            self.image.cropper(
                'setData',
                self.current_model.calc_cropper_placement(
                    self.image.cropper('getImageData')
                )
            );
        },

        switch_focus: function(model, view) {
            var self = this;
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
            // Used for Selenium tests
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

        new zeit.content.image.browser.VariantList();
        zeit.content.image.VARIANTS.fetch({reset: true}).done(function() {
            var view = new zeit.content.image.browser.VariantEditor();
            view.prepare();
        });

    });

})();
