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

        var method = self[action.getAttribute('action')];
        var params = [];
        for (var i = 0; i < action.attributes.length - 1; i++) {
            attr = action.attributes[i];
            if (attr.name.indexOf('cms:param') == 0) params.push(attr);
        }
        params.sort(function(a, b) { return a.name.localeCompare(b.name); });
        params = params.map(function(x) { return x.value; });
        params.unshift(result);

        var d = method.apply(self, params);
        d.addCallbacks(
            function(result) {
                self.done(action);
                self.work(result);
            },
            function(error) {
                self.error(action, error);
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
            context + '/@@checkin?redirect=False' + params);
    },

    start_job: function(context, action, objectlog) {
        var self = this;
        if (isNull(context)) {
            context = window.context_url;
        }
        console.log(context, action, objectlog);
        var d = MochiKit.Async.loadJSONDoc(context + '/@@' + action);
        d.addCallbacks(function(job) {
            if (job.error) {
                throw new Error('Kann nicht veröffentlichen bzw. zurückziehen: ' + job.error);
            }
            return MochiKit.Async.callLater(
                1, function() {
                    return self.poll_until_complete(context, job, objectlog);
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

    poll_until_complete: function(context, job, objectlog) {
        var self = this;
        var d = MochiKit.Async.loadJSONDoc(
            window.application_url + '/@@job-status', {'job': job});
        // status is defined in celery.result.AsyncResult.state
        d.addCallback(function(status) {
            if (status == 'SUCCESS' || status == 'FAILURE') {
                return self.check_job_error(context, job, objectlog);
            }
            // XXX check for error cases as well.
            return MochiKit.Async.callLater(
                1, bind(self.poll_until_complete, self),
                context, job, objectlog);
        });
        d.addErrback(function(err) { zeit.cms.log_error(err); return err; });
        return d;
    },

    check_job_error: function(context, job, objectlog) {
        var self = this;
        if (isUndefinedOrNull(objectlog)) {
            objectlog = 'False';
        }
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            context + '/@@flash-job-errors',
            {'job': job, 'objectlog': objectlog});
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

    error: function(element, error) {
        var message = error.message;
        if (error.req) {
            message = error.req.responseText;
        }
        element = $(element);
        element.removeClass('busy');
        element.addClass('error');
        element.append('<p>' + message + '</p>');
    },

    close: function(context) {
        zeit.cms.current_lightbox.close();
    }
});

}(jQuery));
