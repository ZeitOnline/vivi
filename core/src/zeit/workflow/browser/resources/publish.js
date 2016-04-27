(function($) {

zeit.cms.declare_namespace('zeit.workflow.publish');

zeit.workflow.publish.Publisher = gocept.Class.extend({

    construct: function(worklist) {
        var self = this;
        self.worklist = $('#' + worklist).find('li').toArray();
        self.work(null);
    },

    work: function(result) {
        var self = this;
        var action = self.worklist.shift();
        self.busy(action);
        var override_result = action.getAttribute('cms:context');
        if (override_result) {
            result = override_result;
        }
        var d = self[action.getAttribute('action')](result);
        d.addCallbacks(
            function(result) {
                self.done(action);
                self.work(result);
            },
            function(error) {
                self.error(action, error.message);
                throw error;
            });
    },

    checkin: function(context, params) {
        var self = this;
        if (isUndefinedOrNull(params)) {
            params = '';
        }
        if (isUndefinedOrNull(context)) {
            context = window.context_url;
        }
        return self._redirect_step(
            context + '/@@checkin?redirect=False&event:boolean=' + params);
    },

    // XXX kludgy. Generalize with arguments declared on the <li>?
    checkin_auto_lsc: function(context) {
        var self = this;
        return self.checkin(context, '&semantic_change=None');
    },

    publish: function(context) {
        var self = this;
        return self._start_job(context, 'publish');
    },

    retract: function(context) {
        var self = this;
        return self._start_job(context, 'retract');
    },

    _start_job: function(context, action) {
        var self = this;
        if (isNull(context)) {
            context = window.context_url;
        }
        var d = MochiKit.Async.loadJSONDoc(context + '/@@' + action);
        d.addCallbacks(function(job) {
            if (job == false) {
                throw new Error('500 Internal Server Error');
            }
            return MochiKit.Async.callLater(
                1, function() {
                    return self.poll_until_complete(context, job);
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

    poll_until_complete: function(context, job) {
        var self = this;
        var d = MochiKit.Async.loadJSONDoc(
            context + '/@@job-status', {'job': job});
        // status is defined in lovely.remotetask.interfaces
        d.addCallback(function(status) {
            if (status == 'completed') {
                return self.check_job_error(context, job);
            }
            // XXX check for error cases as well.
            return MochiKit.Async.callLater(
                1, bind(self.poll_until_complete, self), context, job);
        });
        d.addErrback(function(err) { zeit.cms.log_error(err); return err; });
        return d;
    },

    check_job_error: function(context, job) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            context + '/@@flash-job-errors', {'job': job});
        d.addErrback(function(err) { zeit.cms.log_error(err); return err; });
        return d;
    },

    checkout: function(context) {
        var self = this;
        var d = self._redirect_step(context + '/@@checkout?redirect=False');
        d.addCallback(function(result) {
            return result + '/@@edit.html';
        });
        return d;
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
        $(element).addClass('busy');
    },

    done: function(element) {
        $(element).removeClass('busy');
        $(element).addClass('done');
    },

    error: function(element) {
        $(element).removeClass('busy');
        $(element).addClass('error');
    },

    close: function(context) {
        zeit.cms.current_lightbox.close();
    }
});

}(jQuery));
