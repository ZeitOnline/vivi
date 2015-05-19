/*global zeit,Backbone,window,document,jQuery*/
(function($) {

    "use strict";

    zeit.cms.declare_namespace('zeit.content.image');
    zeit.cms.declare_namespace('zeit.content.image.browser');


    /* MODELS */

    zeit.content.image.Variant = Backbone.Model.extend({});


    zeit.content.image.VariantList = Backbone.Collection.extend({

        model: zeit.content.image.Variant,
        url: window.context_url + '/variants'

    });


    zeit.content.image.VARIANTS = new zeit.content.image.VariantList();


    /* VIEWS */

    zeit.content.image.browser.Variant = Backbone.View.extend({

        render: function() {
            var self = this,
                content = $('<img class="preview" src="' + self.model.get('url') + '"/>');
            self.$el.replaceWith(content);
            self.setElement(content);

            if (self.model.has('css')) {
                self.$el.removeClass('preview');
                self.$el.addClass(self.model.get('css'));
            }

            if (self.model.has('width')) {
                self.$el.width(self.model.get('width'));
            }

            return self;
        }
    });


    zeit.content.image.browser.VariantList = Backbone.View.extend({

        el: '#variant-preview',

        initialize: function() {
            this.listenTo(zeit.content.image.VARIANTS, 'reset', this.reset);
        },

        reset: function() {
            var self = this;
            $(zeit.content.image.VARIANTS.models).each(function(index, variant) {
                var view = new zeit.content.image.browser.Variant({model: variant});
                self.$el.append(view.render().el);
            });
        }

    });


    zeit.content.image.browser.VariantEditor = Backbone.View.extend({

        el: '#variant-inner',

        render: function() {
            var self = this;
            var view = new zeit.content.image.browser.Variant({model: self.model});
            self.$el.append(view.render().el);
            self.$el.append('<div class="circle"></div>');
            self.$el.find('div.circle').draggable();
        }
    });


    $(document).ready(function() {
        if (!$('#variant-content').length) {
            return;
        }

        new zeit.content.image.browser.VariantList();
        zeit.content.image.VARIANTS.fetch({reset: true});

        var view = new zeit.content.image.browser.VariantEditor(
            {model: new zeit.content.image.Variant(
                {url: window.master_image_url, css: 'master'})});
        view.render();
    });

})(jQuery);