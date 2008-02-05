// Copyright (c) 2007-2008 gocept gmbh & co. kg
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

    var hideToggle = getFirstElementByTagAndClassName('div', 'hideText', messages);
    connect(hideToggle, 'onclick', function(event) {
        toggleElementClass('hiddenMessages', messages);
    });
    connect(showtoggle, 'onclick', function(event) {
        toggleElementClass('hiddenMessages', messages);
    });

    
});
