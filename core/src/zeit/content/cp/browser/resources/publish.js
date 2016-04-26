zeit.cms.declare_namespace('zeit.content.cp.publish');

zeit.content.cp.publish.Publisher = gocept.Class.extend({
    construct: function() {
        var self = this;
        self.checkin(context_url);
    },

    checkin: function(context) {
        var self = this;
        self._redirect_step(
            context + '/@@checkin?redirect=False&event:boolean=', 'checkin',
            bind(self.publish, self));
    },

    publish: function(context) {
        var self = this;
        self.checked_in = context;
        self.busy('publish');

        var d = MochiKit.Async.loadJSONDoc(context + '/@@publish');
        d.addCallback(function(job) {
            if (job == false) {
                self.error('publish');
                $('publish.errors').innerHTML = 'Automatisches Veröffentlichen nicht möglich';
            } else {
                MochiKit.Async.callLater(
                    1, bind(self.poll_until_publish_complete, self), context, job);
            }
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
    },

    poll_until_publish_complete: function(context, job) {
        var self = this;
        var d = MochiKit.Async.loadJSONDoc(
            context + '/@@publish-status', {'job': job});
        // status is defined in lovely.remotetask.interfaces
        d.addCallback(function(status) {
            if (status == 'completed') {
                self.check_publish_error(context, job);
            } else {
                MochiKit.Async.callLater(
                    1, bind(self.poll_until_publish_complete, self),
                    context, job);
            }
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
    },

    check_publish_error: function(context, job) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            context + '/@@flash-publish-errors', {'job': job});
        d.addCallback(function(result) {
            self.done('publish');
            self.checkout(self.checked_in);
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
    },

    checkout: function(context) {
        var self = this;
        self._redirect_step(
        context + '/@@checkout?redirect=False&came_from=view.html');
    },

    reload_editor: function(url) {
        document.location = url + '/@@edit.html';
    },

    _redirect_step: function(url, step, next) {
        var self = this;
        self.busy(step);
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        d.addCallback(function(result) {
            self.done(step);
            next(result.responseText);
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
    },

    busy: function(step) {
        MochiKit.DOM.addElementClass($('publish.' + step), 'busy');
    },

    done: function(step) {
        MochiKit.DOM.removeElementClass($('publish.' + step), 'busy');
        MochiKit.DOM.addElementClass($('publish.' + step), 'done');
    },

    error: function(step) {
        MochiKit.DOM.removeElementClass($('publish.' + step), 'busy');
        MochiKit.DOM.addElementClass($('publish.' + step), 'error');
    }
});
