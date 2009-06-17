// Copyright (c) 2007-2009 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(window, 'onload', function(event) {
    // Connect messages hide/show
    var showtoggle = $('messages_toggle')
    var messages = $('messages')

    if (messages == null) {
        // no messages, nothing do to
        return
    }

    var errors = getElementsByTagAndClassName('li', 'error', messages)
    var timeout = 0.5;
    if (errors.length > 0) {
        timeout = 5;
    }

    var d = callLater(timeout, function() {
        fade(messages, {
            afterFinish: function() {
                addElementClass(messages, 'hiddenMessages');
                // remove opacity and display from fade
                messages.setAttribute('style', '');
                },
            });
    });

    connect(messages, 'onclick', function(event) {
        d.cancel();
        addElementClass(messages, 'hiddenMessages');
    });
    connect(showtoggle, 'onclick', function(event) {
        d.cancel();
        toggleElementClass('hiddenMessages', messages);
    });

});
