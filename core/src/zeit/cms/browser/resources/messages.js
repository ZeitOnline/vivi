// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$


connect(window, 'onload', function(event) {
    // Connect messages hide/show
    
    var messages = $('messages')
    if (messages == null) {
        // no messages, nothing do to
        return
    }

    connect(messages, 'onclick', function(event) {
        toggleElementClass('hiddenMessages', messages);
    });

    
});
