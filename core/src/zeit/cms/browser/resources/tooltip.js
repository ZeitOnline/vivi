// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.ToolTip = Class.extend({
    
    construct: function(context, url_getter) {
        this.context = context
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
                    othis.showToolTip(
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

    showToolTip: function(text, where) {
        var othis = this;
        var body = $('body');
        var div = DIV({'id': 'tooltip'});
        div.innerHTML = text;
        MochiKit.Style.setElementPosition(div, where);
        body.appendChild(div);

        var signals = [];
        signals.push(
            MochiKit.Signal.connect(
                this.context, 'onmousemove', function(event) {
                    othis.hideToolTip(signals);
        }));
        signals.push(
            MochiKit.Signal.connect(
                'tooltip', 'onmousemove', function(event) {
                    othis.hideToolTip(signals);
        }));
    },

    hideToolTip: function(signals) {
        forEach(signals, function(signal) {
            MochiKit.Signal.disconnect(signal);
        });
        $('tooltip').parentNode.removeChild($('tooltip'));
    },


});

