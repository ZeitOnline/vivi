(function() {

zeit.cms.declare_namespace('zeit.edit');

zeit.edit.getParentComponent = function(context_element) {
    var parent = null;
    var parent_element = context_element.parentNode;
    while (!isNull(parent_element) && isUndefinedOrNull(parent)) {
        parent = parent_element.__handler__;
        parent_element = parent_element.parentNode;
    }
    return parent;
};


zeit.edit.Editor = gocept.Class.extend({

    __name__: 'zeit.edit.Editor',

    construct: function() {
        var self = this;
        self.content = $('cp-content');
        self.content.__handler__ = self;
        self.busy = false;
        MochiKit.Signal.connect(
            'content', 'onclick',
            self, self.handleContentClick);
        MochiKit.Signal.connect(
            self, 'reload', self, self.reload);
        MochiKit.Signal.connect(
            self, 'reload-editor', self, self.load_editor);
        new zeit.cms.ToolTipManager(self.content);
    },

    handleContentClick: function(event) {
        var self = this;
        var target = event.target();
        var module_name = null;
        log("Target " + target.nodeName);
        while (!isNull(target) && target.id != 'content') {
            // Target can be null when it was removed from the DOM by a
            // previous event handler (like the lightbox shade)
            module_name = target.getAttribute('cms:cp-module');
            if (!isNull(module_name)) {
                break;
            }
            target = target.parentNode;
        }
        if (!module_name && event.target().nodeName == 'A'
            && event.target().target) {
            return;
        }

        if (module_name) {
            log("Loading module " + module_name);
            event.stop();
            var module = zeit.cms.resolveDottedName(module_name);
            new module(target);
        } else if (event.target().nodeName == 'A') {
            event.preventDefault();
        }
    },

    load_editor: function(){
        var self = this;
        return self.reload('cp-content-inner', context_url + '/contents');
    },

    reload: function(element_id, url) {
        var self = this;
        log("Reloading", element_id, url);
        var element = $(element_id);
        MochiKit.Signal.signal(self, 'before-reload');
        var d = zeit.cms.with_lock(
            MochiKit.Async.doSimpleXMLHttpRequest, url);
        d.addCallback(function(result) {
            return self.replace_element(element, result);
        });
        d.addCallback(function(result) {
            // Result: replaced element
            return zeit.cms.evaluate_js_and_css(result);
        });
        d.addCallback(function(result) {
            MochiKit.Signal.signal(window, 'script-loading-finished', self);
            return result;
        });
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self, 'after-reload');
            MochiKit.Signal.signal(window, 'changed');
            return result;
        });
        d.addErrback(function(error) {
            zeit.cms.log_error(error);
            return error;
        });
        return d;
    },

    replace_element: function(element, result) {
        var self = this;
        var dom = DIV();
        dom.innerHTML = result.responseText;
        return MochiKit.DOM.swapDOM(element, dom.firstChild);
    },

    busy_until_reload_of: function(component, delay) {
        var self = this;
        if (self.busy) {
            // Already busy
            return;
        }
        log("Entering BUSY state " + component.__name__);
        self.busy = true;
        MochiKit.Signal.signal(self, 'busy', delay);
        var ident = MochiKit.Signal.connect(
            component, 'after-reload', function() {
                MochiKit.Signal.disconnect(ident);
                self.idle();
        });
    },

    idle: function() {
        var self = this;
        log("Entering IDLE state");
        if (self.busy) {
            self.busy = false;
            MochiKit.Signal.signal(self, 'idle');
        }
    }
});


}());


(function() {
    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        if (isNull($('cp-content'))) {
            return;
        }
        // There is only one instance per page. Put it under a well known
        // location
        zeit.edit.editor = new zeit.edit.Editor();
        zeit.edit.create_tabs();
        MochiKit.Signal.signal(window, 'cp-editor-initialized');
        zeit.edit.editor.busy_until_reload_of(
            zeit.edit.editor, 0);
        var d = zeit.edit.editor.load_editor();
        d.addCallback(function(result) {
            MochiKit.Signal.signal(window, 'cp-editor-loaded');
            return result;
        });
    });
}());


zeit.edit.create_tabs = function() {
    var tabs = new zeit.cms.Tabs('cp-forms');
    tabs.add(new zeit.cms.Tab('cp-search', 'Inhalte'));
    tabs.add(new zeit.cms.Tab('cp-library', 'Module'));
    // XXX missing concept how JS knows about repository/workingcopy
    if (window.location.href.indexOf('/repository/') == -1) {
        tabs.add(new zeit.cms.Tab('cp-undo', 'Undo'));
    }
};


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    MochiKit.DOM.addElementClass('cp-search', 'zeit-find-search');
    zeit.find.init_full_search();
});


zeit.edit.BusyIndicator = gocept.Class.extend({

    construct: function() {
        var self = this;
        MochiKit.Signal.connect(
            zeit.edit.editor, 'busy', self, self.busy_after_a_while);
        MochiKit.Signal.connect(
            zeit.edit.editor, 'idle', self, self.idle);
        self.delayer = null;
        self.indicator = DIV({
            'class': 'hidden',
            'id': 'busy-indicator'},
            DIV({'class': 'shade'}),
            IMG({'src': application_url + '/@@/zeit.cms/loading.gif'})
            );
        $('content').appendChild(self.indicator);
    },

    busy_after_a_while: function(delay) {
        var self = this;
        if (isUndefinedOrNull(delay)) {
            delay = 1;
        }
        self.delayer = MochiKit.Async.callLater(delay, function() {
            self.busy();
        });
    },

    busy: function() {
        var self = this;
        MochiKit.Style.setOpacity(self.indicator, 0);
        MochiKit.DOM.removeElementClass(self.indicator, 'hidden');
        MochiKit.Visual.appear(self.indicator);
    },

    idle: function() {
        var self = this;
        if (!isNull(self.delayer)) {
            self.delayer.cancel();
            self.delayer = null;
        }
        MochiKit.DOM.addElementClass(self.indicator, 'hidden');
    }

});


(function() {
    var ident = MochiKit.Signal.connect(
        window, 'cp-editor-initialized',
        function() {
            MochiKit.Signal.disconnect(ident);
            zeit.edit.busy_indicator = new zeit.edit.BusyIndicator();
        });
}());


// cms:cp-module handlers

zeit.edit.LoadAndReload = gocept.Class.extend({

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        var d = zeit.edit.makeJSONRequest(url);
        return d;
    }

});


zeit.edit.follow_link = function(element) {
    MochiKit.Async.callLater(
        zeit.cms.SubPageForm.SUBMIT_DELAY_FOR_FOCUS + 0.1,
        function() {
            zeit.cms.with_lock(function(url) {
                console.log('zeit.edit.follow_link ', url);
                window.location.href = url;
        }, element.href);
    });
};