zeit.content.cp.publish = {};


zeit.content.cp.publish.Publisher = Class.extend({
    construct: function() {
        var self = this;
        self.steps = [
            self.checkin,
            self.publish,
            self.poll,
            self.check_error,
            self.checkout,
            self.reload_editor,
        ];
        self.step = 0;
        self.next(context_url);
    },

    next: function(url) {
        var self = this;
        if (self.step >= self.steps.size)
            return;
        self.steps[self.step].call(self, url);
        self.step++;
    },

    checkin: function(context) {
        var self = this;
        self._async_step(context + '/@@checkin?redirect=False', 'checkin');
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
                self.next(job);
            }
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
    },

    poll: function(job) {
        var self = this;
        var d = MochiKit.Async.loadJSONDoc(
            application_url + '/@@publish-status', {'job': job});
        // status is defined in lovely.remotetask.interfaces
        d.addCallback(function(status) {
            if (status == 'completed') {
                self.next(job);
            } else {
                MochiKit.Async.callLater(5, bind(self.poll, self), job);
            }
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
    },

    check_error: function(job) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            application_url + '/@@flash-publish-errors', {'job': job});
        d.addCallback(function(result) {
            self.done('publish');
            self.next(self.checked_in);
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
    },

    checkout: function(context) {
        var self = this;
        self._async_step(context + '/@@checkout?redirect=False', 'checkout');
    },

    reload_editor: function(url) {
        document.location = url + '/@@edit.html';
    },

    _async_step: function(url, step) {
        var self = this;
        self.busy(step);
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        d.addCallback(function(result) {
            self.done(step);
            self.next(result.responseText);
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err});
    },

    busy: function(step) {
        addElementClass($('publish.' + step), 'busy');
    },

    done: function(step) {
        removeElementClass($('publish.' + step), 'busy');
        addElementClass($('publish.' + step), 'done');
    },

    error: function(step) {
        removeElementClass($('publish.' + step), 'busy');
        addElementClass($('publish.' + step), 'error');
    },
});
