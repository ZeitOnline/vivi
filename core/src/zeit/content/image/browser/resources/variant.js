/*global zeit,Backbone,window,document,jQuery*/
(function($) {

    "use strict";

    zeit.cms.declare_namespace('zeit.content.image');
    zeit.cms.declare_namespace('zeit.content.image.browser');


    /* MODELS */

    zeit.content.image.Variant = Backbone.Model.extend({
        urlRoot: window.context_url + '/variants'
    });


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

        events: {
            "dragstop .focuspoint": "save"
        },

        initialize: function() {
            var self = this;
            self.model = new zeit.content.image.Variant({id: 'default'});
            self.model.fetch().done(function() {
                self.render();
            });
        },

        render: function() {
            var self = this;
            var view = new zeit.content.image.browser.Variant({model: self.model});
            self.$el.append(view.render().el);
            self.image = self.$('img');

            self.circle = $('<div class="focuspoint"><div class="circle"></div></div>');
            self.circle.css('top', self.model.get('focus_y') * 100 + '%');
            self.circle.css('left', self.model.get('focus_x') * 100 + '%');

            self.$el.append(self.circle);
            self.circle.draggable();
        },

        save: function() {
            var self = this;
            var focus_x = ((self.circle.position().left) / self.image.width());
            var focus_y = ((self.circle.position().top) / self.image.height());
            self.model.save({"focus_x": focus_x, "focus_y": focus_y});
        }
    });


    $(document).ready(function() {
        if (!$('#variant-content').length) {
            return;
        }

        new zeit.content.image.browser.VariantList();
        zeit.content.image.VARIANTS.fetch({reset: true}).done(function() {
            new zeit.content.image.browser.VariantEditor();
        });

    });

})(jQuery);