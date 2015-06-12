/*global zeit,Backbone,window,document*/
(function() {
    "use strict";

    var $ = window.jQuery;
    var _ = window.Underscore;

    zeit.cms.declare_namespace('zeit.content.image');
    zeit.cms.declare_namespace('zeit.content.image.browser');


    /* MODELS */

    zeit.content.image.Variant = Backbone.Model.extend({
        urlRoot: window.context_url + '/variants',

        make_url: function() {
            var self = this,
                url = self.get('url');
            return url + '?nocache=' + new Date().getTime();
        }
    });


    zeit.content.image.VariantList = Backbone.Collection.extend({

        model: zeit.content.image.Variant,
        url: window.context_url + '/variants'

    });


    zeit.content.image.VARIANTS = new zeit.content.image.VariantList();


    /* VIEWS */

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

    zeit.content.image.browser.PreviewVariant = AbstractVariant.extend({

        create_image: function() {
            var self = this,
                image = AbstractVariant.prototype.create_image.apply(this);

            image.addClass('preview');

            // Set max-width defined in config as width to display smaller
            // sizes of a variant as big as allowed.
            if (self.model.has('max_size')) {
                var size = self.model.get('max_size').split('x');
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


    zeit.content.image.browser.EditableVariant = AbstractVariant.extend({

        create_image: function() {
            var self = this,
                image = AbstractVariant.prototype.create_image.apply(this);

            image.addClass('editor');

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
                    new zeit.content.image.browser.EditableVariant(self.default_model)
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

            self.circle = $('<div class="focuspoint"><div class="circle"></div></div>');
            self.$el.append(self.circle);
            self.circle.draggable({
                containment: self.$el
            });

            $('#slider').slider({
                min: 1,
                max: 100,
                value: self.current_model.get('zoom') * 100
            });

            $('#slider').on('slidestop', function() {
                self.save();
            });

            self.update();
        },

        save: function() {
            var self = this;
            var focus_x = ((self.circle.position().left) / self.image.width());
            var focus_y = ((self.circle.position().top) / self.image.height());
            var zoom = $('#slider').slider("value") / 100;
            self.current_model.save(
                {"focus_x": focus_x, "focus_y": focus_y, "zoom": zoom}
            ).done(function() {
                self.update();  // overwrite absolute positioning of focuspoint
                zeit.content.image.VARIANTS.trigger('reload');
                self.notify_status("saved");
            });
        },

        update: function() {
            var self = this;
            self.circle.css('top', self.current_model.get('focus_y') * 100 + '%');
            self.circle.css('left', self.current_model.get('focus_x') * 100 + '%');
            $('#slider').slider("value", self.current_model.get('zoom') * 100);
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
