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
        toggleElementClass('hiddenMessages', messages);
    });
    connect(showtoggle, 'onclick', function(event) {
        toggleElementClass('hiddenMessages', messages);
    });

    new TimerWidget("messages_counter", 5,
        function(){
            toggleElementClass('hiddenMessages', messages);
        });

});


var TimerWidget = Class.extend({

    construct: function(widget_id, seconds, func_on_stop) {
        this.widget_id = widget_id;
        this.widget = $(widget_id);
        this.element = getFirstElementByTagAndClassName('span', 'Counter');
        this.seconds = seconds
        this.timer = null;
        this.onStopFunction = func_on_stop;
        this.startTimer();
    },

    startTimer: function() {
        this.element.innerHTML = this.seconds
        this.timer = callLater(1, this.count, this);
    },

    count: function(othis) {
        othis.element.innerHTML = othis.seconds
        othis.seconds--
        othis.timer.cancel()
        if (othis.seconds >= 0)
            othis.timer = callLater(1, othis.count, othis);
        else
            othis.onStop();
    },

    onStop: function() {
        this.onStopFunction();
        hideElement(this.widget);
    }

});
