zeit.cms.declare_namespace('zeit.workflow.publish');

zeit.workflow.publish.Publisher = gocept.Class.extend({

    construct: function(worklist) {
        var self = this;
        self.worklist = MochiKit.DOM.getElementsByTagAndClassName(
            'li', null, worklist);
        self.work(null);
    },

    work: function(result) {
        var self = this;
        var action = self.worklist.shift();
        self.busy(action);
        var d = self[action.getAttribute('action')](result);
        d.addCallbacks(
            function(result) {
                self.done(action);
                self.work(result);
            },
            function(error) {
                self.error(error.message);
                throw error;
            });
    },

    checkin: function(context) {
        var self = this;
        if (isUndefinedOrNull(context)) {
            context = window.context_url;
        }
        return self._redirect_step(
            context + '/@@checkin?redirect=False&event:boolean=');
    },

    publish: function(context) {
        var self = this;
        if (isNull(context)) {
            context = window.context_url;
        }
        var d = MochiKit.Async.loadJSONDoc(context + '/@@publish');
        d.addCallbacks(function(job) {
            if (job == false) {
                throw new Error('Veröffentlichen nicht möglich');
            }
            return MochiKit.Async.callLater(
                1, function() {
                    return self.poll_until_publish_complete(job)
                });
            },
            function(err) {
                zeit.cms.log_error(err);
                return err;
            });
        d.addCallback(function(result) {
            return context;
        });
        return d;
    },

    poll_until_publish_complete: function(job) {
        var self = this;
        var d = MochiKit.Async.loadJSONDoc(
            application_url + '/@@publish-status', {'job': job});
        // status is defined in lovely.remotetask.interfaces
        d.addCallback(function(status) {
            if (status == 'completed') {
                return self.check_publish_error(job);
            }
            // XXX check for error cases as well.
            return MochiKit.Async.callLater(
                1, bind(self.poll_until_publish_complete, self), job);
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
        return d;
    },

    check_publish_error: function(job) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            application_url + '/@@flash-publish-errors', {'job': job});
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
        return d;
    },

    checkout: function(context) {
        var self = this;
        return self._redirect_step(context + '/@@checkout?redirect=False');
    },

    reload: function(context) {
        var self = this;
        if (isUndefinedOrNull(context)) {
            context = window.context_url;
        }
        document.location = context;
        // return a deferred which is never fired. This keeps the entry busy
        // until the page is reloaded.
        return new MochiKit.Async.Deferred();
    },

    _redirect_step: function(url) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        d.addCallbacks(
            function(result) {
                return result.responseText;
            },
            function(err) {
                zeit.cms.log_error(err);
                return err;
            });
        return d;
    },

    busy: function(element) {
        MochiKit.DOM.addElementClass(element, 'busy');
    },

    done: function(element) {
        MochiKit.DOM.removeElementClass(element, 'busy');
        MochiKit.DOM.addElementClass(element, 'done');
    },

    error: function(step) {
        MochiKit.DOM.removeElementClass(element, 'busy');
        MochiKit.DOM.addElementClass(element, 'error');
    },
});

