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

    zeit.content.image.browser.Variant = Backbone.View.extend({

        img_css_class: 'preview',

        render: function() {
            var self = this;
            var content = $(_.template('<img class="{{css}}"/>')({
                    css: self.img_css_class}));

            content.on('load', function() {
                self.trigger('render');
            });

            content.attr('src', self.model.make_url());
            self.$el.replaceWith(content);
            self.setElement(content);

            if (self.model.has('css')) {
                self.$el.removeClass('preview');
                self.$el.addClass(self.model.get('css'));
            }

            if (self.model.has('width')) {
                self.$el.width(self.model.get('width'));
            }

            if (self.model.has('max-size')) {
                var size = self.model.get('max-size').split('x');
                self.$el.width(size[0]);
            }

            self.$el.on('click', function() {
                self.model.trigger('switch-focus', self.model, self);
            });

            return self;
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
            this.model_views = [];
        },

        reset: function() {
            var self = this;
            self.$el.empty();
            zeit.content.image.VARIANTS.each(function(variant) {
                var view = new zeit.content.image.browser.Variant(
                    {model: variant}
                );
                self.model_views.push(view);
                self.$el.append(view.render().el);
            });
        },

        reload: function() {
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
            self.model_view = new zeit.content.image.browser.Variant(
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
                    new zeit.content.image.browser.Variant(self.default_model)
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
            self.circle.draggable();

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
                zeit.content.image.VARIANTS.trigger('reload');
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
            });
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
