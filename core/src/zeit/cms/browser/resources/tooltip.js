// Copyright (c) 2007-2009 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.showToolTip = function(context, text, where) {
    var othis = this;
    var body = $('body');
    var div = DIV({'id': 'tooltip'});
    div.innerHTML = text;
    where.x += 10;
    where.y += 10;
    MochiKit.Style.setElementPosition(div, where);
    body.appendChild(div);

    var signals = [];
    signals.push(
        MochiKit.Signal.connect(
            context, 'onmouseout', function(event) {
                zeit.cms.hideToolTip(signals);
    }));
    signals.push(
        MochiKit.Signal.connect(
            'tooltip', 'onmousemove', function(event) {
                zeit.cms.hideToolTip(signals);
    }));
};


zeit.cms.hideToolTip = function(signals) {
    forEach(signals, function(signal) {
        MochiKit.Signal.disconnect(signal);
    });
    $('tooltip').parentNode.removeChild($('tooltip'));
};


zeit.cms.ToolTip = Class.extend({

    construct: function(context, url_getter) {
        this.context = $(context);
        this.url_getter = url_getter;

        this.mouse_over_deferred = null;

        connect(context, 'onmouseover', this, 'handleMouseOver');
        connect(context, 'onmouseout', this, 'handleMouseOut');
    },

    handleMouseOver: function(event) {
        var othis = this;
        if (this.mouse_over_deferred !== null) {
            return;
        }
        MochiKit.Logging.log("Start waiting for tooltip");
        this.mouse_over_deferred = MochiKit.Async.callLater(
            0.4, function(result) {
                othis.mouse_over_deferred = null;
                var url = othis.url_getter();
                if (url === null) {
                    MochiKit.Logging.log('Not loading tooltip, got no URL');
                    return;
                }
                MochiKit.Logging.log('Loading tooltip from ' + url);
                var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
                d.addCallback(function(result) {
                    zeit.cms.showToolTip(
                        othis.context,
                        result.responseText, event.mouse().client);
                    return result;
                });
        });
    },

    handleMouseOut: function(event) {
        if (this.mouse_over_deferred === null) {
            return;
        }
        MochiKit.Logging.log('Cancelled tooltip.');
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

zeit.cms.ToolTipManager = Class.extend({
    construct: function(context) {
        var othis = this;
        othis.context = context;
        connect(context, 'onmouseover', this, 'handleMouseOver');
    },

    handleMouseOver: function(event) {
        var othis = this;
        var target = event.target();
        while (!target.hasAttribute('cms:tooltip') && target != othis.context) {
            target = target.parentNode;
        }
        var tooltip = target.getAttribute('cms:tooltip');
        if (tooltip) {
            zeit.cms.showToolTip(target, tooltip, event.mouse().client);
        }
    },
});
