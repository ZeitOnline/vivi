// Copyright (c) 2007-2010 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.showToolTip = function(context, text, where) {
    var body = $('body');
    var div = $('tooltip');
    if (!isNull(div)) {
        zeit.cms.hideToolTip(div.signals);    
    }
    div = DIV({'id': 'tooltip'});
    div.innerHTML = text;
    where.x += 10;
    where.y += 10;
    MochiKit.Style.setElementPosition(div, where);
    body.appendChild(div);

    div.signals = [];
    div.signals.push(
        MochiKit.Signal.connect(
            context, 'onmouseout', function(event) {
                zeit.cms.hideToolTip(div.signals);
    }));
    div.signals.push(
        MochiKit.Signal.connect(
            'tooltip', 'onmousemove', function(event) {
                zeit.cms.hideToolTip(div.signals);
    }));
};


zeit.cms.hideToolTip = function(signals) {
    while (signals.length) {
        MochiKit.Signal.disconnect(signals.pop());
    }
    $('tooltip').parentNode.removeChild($('tooltip'));
};


zeit.cms.ToolTip = gocept.Class.extend({

    construct: function(context, url_getter) {
        var self = this;
        self.context = $(context);
        self.url_getter = url_getter;
        self.events = []

        self.mouse_over_deferred = null;

        self.events.push(MochiKit.Signal.connect(
            context, 'onmouseover',
            self, self.handleMouseOver));
        self.events.push(MochiKit.Signal.connect(
            context, 'onmouseout', self, self.handleMouseOut));
    },

    destruct: function() {
        var self = this;
        while (self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        }
    },

    handleMouseOver: function(event) {
        var othis = this;
        if (this.mouse_over_deferred !== null) {
            return;
        }
        if (!isUndefinedOrNull(
            MochiKit.DragAndDrop.Draggables.activeDraggable)) {
            return;
        }
        this.mouse_over_deferred = MochiKit.Async.callLater(
            0.4, function(result) {
                othis.mouse_over_deferred = null;
                var url = othis.url_getter(event);
                if (url === null) {
                    return;
                }
                if (url.indexOf('tooltip:') == 0) {
                    zeit.cms.showToolTip(
                        othis.context,
                        url.substring('tooltip:'.length),
                        event.mouse().client);
                } else {
                    var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
                    d.addCallback(function(result) {
                        zeit.cms.showToolTip(
                            othis.context,
                            result.responseText, event.mouse().client);
                        return result;
                    });
                }
        });
    },

    handleMouseOut: function(event) {
        if (this.mouse_over_deferred === null) {
            return;
        }
        this.mouse_over_deferred.cancel();
        this.mouse_over_deferred = null;
    },
});


zeit.cms.LinkToolTip = zeit.cms.ToolTip.extend({

    construct: function(context) {
        var othis = this;
        var url_getter = function() {
            return othis.getURLFromLink()
        }
        arguments.callee.$.construct.call(othis, context, url_getter);
    },

    getURLFromLink: function() {
        var othis = this;
        var url = othis.context.href;
        if (!url) {
            return null;
        }
        return url + '/@@drag-pane.html';
    },
});


zeit.cms.TextToolTip = zeit.cms.ToolTip.extend({

    construct: function(context) {
        var self = this;
    },

});


zeit.cms.ToolTipManager = zeit.cms.ToolTip.extend({

    construct: function(context) {
        var self = this;
        self.context = context;
        url_getter = function(event) {
            return self.getURL(event);
        }
        arguments.callee.$.construct.call(self, context, url_getter);
    },

    getURL: function(event) {
        var self = this;
        var target = event.target();
        while (!target.hasAttribute('cms:tooltip') && target != self.context) {
            target = target.parentNode;
        }
        var tooltip = target.getAttribute('cms:tooltip');
        if (!tooltip) {
            return null;
        }
        return 'tooltip:' + tooltip;
    },
});
