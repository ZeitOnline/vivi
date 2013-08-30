"use strict";

(function($) {

zeit.cms.MobileAlternativeWidget = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        self.container = element;
        $(self.container).on(
            'click', MochiKit.Base.bind(self.handle_click, self));
    },

    handle_click: function(event) {
        var self = this;
        var method = $(event.target).attr('cms:call');
        if (! method) {
            return;
        }
        method = self[method];
        method.call(self, event);
        event.preventDefault();
    },

    set_url: function(event) {
        var self = this;
        var url = $(event.target).attr('href');
        var input = $(self.container).find('input');
        input.val(url);
        input.trigger('change');
        input.trigger('focusout');
    }

});


zeit.cms.MobileAlternativeWidget.setup_widgets = function(root) {
    $('.mobile-alternative-widget', root).each(function(i, element) {
        if (! element.widget) {
            element.widget = new zeit.cms.MobileAlternativeWidget(element);
        }
    });
};



$(document).bind('fragment-ready', function(event) {
    zeit.cms.MobileAlternativeWidget.setup_widgets(event.__target);
});

$(document).ready(function() {
    zeit.cms.MobileAlternativeWidget.setup_widgets(document);
});


}(jQuery));