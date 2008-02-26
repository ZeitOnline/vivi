// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(window, 'onload', function(event) {
    // Connect messages hide/show
    var showtoggle = $('messages_toggle')
    var messages = $('messages')
    var hideToggle = getFirstElementByTagAndClassName(
        'div', 'hideText', messages);

    if (hideToggle == null) {
        // no messages, nothing do to
        return
    }

    connect(hideToggle, 'onclick', function(event) {
        addElementClass(messages, 'hiddenMessages');
    });
    connect(showtoggle, 'onclick', function(event) {
        toggleElementClass('hiddenMessages', messages);
    });

    callLater(5, function() {
        fade(messages, {
            afterFinish: function() {
                addElementClass(messages, 'hiddenMessages');
                // remove opacity and display from fade
                messages.setAttribute('style', '');
                },
            });
    });

});
