// Copyright (c) 2012 gocept gmbh & co. kg
// See also LICENSE.txt

(function($) {

zeit.cms.GalleryDetails = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        self.element = $(element);
        self.pos = 0;
        self.entries = $.parseJSON(self.element.attr('cms:data'));
        self.element.bind('click', MochiKit.Base.bind(self.handle_click, self));
        self.change_image(0);
    },

    change_image: function(index) {
        var self = this;
        if (index < 0 || index > self.entries.length - 1) {
            return;
        }
        self.pos = index;
        var url = self.entries[self.pos].url;
        var img = $('img', self.element);
        img.attr('src', url);

        self.update_copyrights();
        self.update_caption();

        $('.gallery_details_pos', self.element).text(self.pos+1);
        $('.gallery_details_max', self.element).text(self.entries.length);
    },

    update_copyrights: function() {
        var self = this;
        var copy = self.entries[self.pos].copyrights;
        var copyright = $('.gallery_details_copyright', self.element);
        copyright.children().remove();
        copy = $(copy).each(function(i, val){
            var html = $('<span></span>');
            if (val[1] != null){
                html = $('<a></a>');
                html.attr('href', val[1]);
            }
            html.append(val[0]);
            copyright.append(html);
        });
    },

    update_caption: function() {
        var self = this;
        var caption = $('.gallery_details_caption', self.element);
        var copy = self.entries[self.pos].caption;
        var caption_html = $('<span></span>');
        caption.children().remove();
        if (caption != null) {
            caption_html.text(copy);
        }
        caption.append(caption_html);
    },

    handle_click: function(event) {
        var self = this;
        var target = $(event.target);
        if (target.hasClass('gallery_details_prev')) {
            self.change_image(self.pos - 1);
        } else if (target.hasClass('gallery_details_next')) {
            self.change_image(self.pos + 1);
        }
    }

});


$(document).bind('fragment-ready', function(event) {
    $('.gallery_details', event.__target).each(function(i, element) {
        element.controller = new zeit.cms.GalleryDetails(element);
    });
});

}(jQuery));
