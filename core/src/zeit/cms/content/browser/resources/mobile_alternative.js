(function($) {
"use strict";


zeit.cms.MobileAlternativeWidget = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        self.container = $(element);
        self.input = self.container.find('input[type="text"]');
        self.checkbox = self.container.find('input[type="checkbox"]');
        self.checkbox.on('click', function() {
            self.input.val('');
        });
        self.input.on('keydown', function() {
            self.checkbox.prop('checked', false);
        });
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
