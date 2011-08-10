// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.MessageView = zeit.cms.View.extend({

    construct: function(url, target_id) {
        var self = this;
        arguments.callee.$.construct.call(self, url, target_id);
        self.events = [];
        self.initialize();
        MochiKit.Signal.connect(
            self, 'load', self, self.initialize);
        MochiKit.Signal.connect(self, 'before-load', function(event) {
            while(self.events.length) {
                MochiKit.Signal.disconnect(self.events.pop());
            };
        });
    },

    initialize: function() {
        var self = this;
        var messages = $('messages');
        if (messages == null) {
            return;
        }
        self.connect_toggle_button();
        self.fadeout();
    },

    fadeout: function() {
        var self = this;
        var messages = $('messages');
        var errors = MochiKit.DOM.getElementsByTagAndClassName(
            'li', 'error', messages);
        var timeout = 0.5;
        if (errors.length > 0) {
            timeout = 5;
        }

        self.fade = callLater(timeout, function() {
            MochiKit.Visual.fade(messages, {
                afterFinish: function() {
                    MochiKit.DOM.addElementClass(messages, 'hiddenMessages');
                    // remove opacity and display from fade
                    messages.setAttribute('style', '');
                    }
                });
        });
    },

    connect_toggle_button: function() {
        var self = this;
        var messages = $('messages');
        var showtoggle = $('messages_toggle');
        self.events.push(MochiKit.Signal.connect(
            messages, 'onclick', function(event) {
            self.fade.cancel();
            MochiKit.DOM.addElementClass(messages, 'hiddenMessages');
        }));
        self.events.push(MochiKit.Signal.connect(
            showtoggle, 'onclick', function(event) {
            self.fade.cancel();
            MochiKit.DOM.toggleElementClass('hiddenMessages', messages);
        }));
    }
});


MochiKit.Signal.connect(window, 'onload', function(event) {
    zeit.cms.messages = new zeit.cms.MessageView(
        application_url + '/@@messages', 'messages_container');
});
