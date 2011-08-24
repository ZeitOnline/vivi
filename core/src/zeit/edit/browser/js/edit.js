(function() {

zeit.cms.declare_namespace('zeit.edit');

// Lock to hold for asynchronous tasks.
zeit.edit.json_request_lock = new MochiKit.Async.DeferredLock();

zeit.edit.with_lock = function(callable) {
    var d = zeit.edit.json_request_lock.acquire();
    var pfunc = MochiKit.Base.partial.apply(
        MochiKit.Base, MochiKit.Base.extend(null, arguments));
    d.addCallback(function(result) {
        return pfunc();
    });
    d.addBoth(function(result_or_error) {
        zeit.edit.json_request_lock.release();
        return result_or_error;
    });
    return d;
};

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
        self.inner_content = null;
        self.content.__handler__ = self;
        self.busy = false;
        MochiKit.Signal.connect(
            'content', 'onclick',
            self, self.handleContentClick);
        MochiKit.Signal.connect(
            self, 'reload', self, self.reload);
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
        if (module_name) {
            if (module_name == 'follow-link') {
                // Follow links if called explicitly.
                return;
            }
            log("Loading module " + module_name);
            event.stop();
            var module = zeit.cms.resolveDottedName(module_name);
            new module(target);
        } else if (event.target().nodeName == 'A' && event.target().target) {
            self = 'pass';
        } else if (event.target().nodeName == 'A') {
            event.preventDefault();
        }
    },

    reload: function(element_id, url) {
        var self = this;
        log("Reloading", element_id, url);
        var element = null;
        if (!isUndefinedOrNull(element_id)) {
             element = $(element_id);
        }
        MochiKit.Signal.signal(self, 'before-reload');
        if (isUndefinedOrNull(url)) {
            url = context_url + '/@@contents';
        }
        var d = zeit.edit.with_lock(
            MochiKit.Async.doSimpleXMLHttpRequest, url);
        if (isNull(element)) {
            d.addCallback(function(result) {
                return self.replace_whole_editor(result);
            });
        } else {
            d.addCallback(function(result) {
                return self.replace_element(element, result);
            });
        }
        d.addCallback(function(result) {
            // Result: replaced element
            var loading = [];
            MochiKit.Iter.forEach(
                MochiKit.DOM.getElementsByTagAndClassName(
                    'SCRIPT', null, result),
                function(script) {
                    loading.push(zeit.cms.import(script.src));
                    MochiKit.DOM.removeElement(script);
                });
            MochiKit.Iter.forEach(
                MochiKit.DOM.getElementsByTagAndClassName(
                    'LINK', null, result),
                function(link) {
                    if (link.rel == 'stylesheet') {
                        loading.push(zeit.cms.import(link.href));
                        MochiKit.DOM.removeElement(link);
                    }
                });
            var dl = new MochiKit.Async.DeferredList(loading);
            return dl;
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

    replace_whole_editor: function(result) {
        var self = this;
        if (isNull(self.inner_content)) {
            self.content.innerHTML = result.responseText;
            self.inner_content = (
                MochiKit.DOM.getFirstElementByTagAndClassName(
                    'div', 'cp-content-inner', self.content));
        } else {
            var dom = DIV();
            dom.innerHTML = result.responseText;
            var new_inner = (
                MochiKit.DOM.getFirstElementByTagAndClassName(
                    'div', 'cp-content-inner', dom));
            self.inner_content.innerHTML = new_inner.innerHTML;
        }
        if (isUndefinedOrNull(self.inner_content)) {
            throw Error("Invalid editor content.");
        }
        return self.inner_content;
    },

    replace_element: function(element, result) {
        var self = this;
        var dom = DIV();
        dom.innerHTML = result.responseText;
        MochiKit.DOM.swapDOM(element, dom.firstChild);
        return element; // XXX
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




(function() {
    var ident = MochiKit.Signal.connect(window, 'onload', function() {
        MochiKit.Signal.disconnect(ident);
        if (isNull($('cp-content'))) {
            return;
        }
        // There is only one instance per page. Put it under a well known
        // location
        zeit.edit.editor = new zeit.edit.Editor();
        MochiKit.Signal.signal(window, 'cp-editor-initialized');
        zeit.edit.editor.busy_until_reload_of(
            zeit.edit.editor, 0);
        var d = zeit.edit.editor.reload();
        d.addCallback(function(result) {
            MochiKit.Signal.signal(window, 'cp-editor-loaded');
            return result;
        });
    });
}());


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
            IMG({'src': application_url + '/@@/zeit.imp/loading.gif'})
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


var wire_forms = function() {
    forEach($$('.inline-form'), function(container) {
        if (MochiKit.DOM.hasElementClass(container, 'wired')) {
            return;
        }
        //XXX need to make it context aware
        var url = container.getAttribute('action');
        container.form = new zeit.cms.SubPageForm(
            url, container, {save_on_change: true});
        MochiKit.DOM.addElementClass(container, 'wired');
    });
};


MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    wire_forms();
});


}());


zeit.edit.LoadAndReload = gocept.Class.extend({

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        var d = zeit.edit.makeJSONRequest(url);
        return d;
    }

});


zeit.edit.LightBoxForm = zeit.cms.LightboxForm.extend({

    __name__: 'zeit.edit.LightBoxForm',
    context: zeit.edit.context.Lightbox,

    construct: function(context_element) {
        var self = this;
        self.context_element = context_element;
        var container_id = context_element.getAttribute('cms:lightbox-in');
        self.parent = zeit.edit.getParentComponent(context_element);
        var url = context_element.getAttribute('href');
        self.reload_id = context_element.getAttribute(
            'cms:lightbox-reload-id');
        self.reload_url = context_element.getAttribute(
            'cms:lightbox-reload-url');
        arguments.callee.$.construct.call(self, url, $(container_id));
        self.lightbox.content_box.__handler__ = self;
        self.reload_parent_component_on_close = true;
        new self.context(self);
    },

    connect: function() {
        var self = this;
        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'before-reload', function() {
                self.reload_parent_component_on_close = false;
                self.close();
        }));
        self.close_event_handle = MochiKit.Signal.connect(
            self.lightbox, 'before-close',
            self, self.on_close);
        self.events.push(
            MochiKit.Signal.connect(
                self, 'reload', self, self.reload));
    },

    disconnect: function() {
        // hum, do we need to do anything here? We use the lightbox events
        // right now.
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        var d = arguments.callee.$.reload.call(self);
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self, 'after-reload');
            return result;
        });
        return d;
    },

    on_close: function() {
        var self = this;
        log("closing lightbox");
        MochiKit.Signal.disconnect(self.close_event_handle);
        MochiKit.Signal.signal(self, 'before-close');
        if (self.reload_parent_component_on_close) {
            MochiKit.Signal.signal(
                self.parent, 'reload',
                self.reload_id, self.reload_url);
        }
    }
});


zeit.edit.TabbedLightBoxForm = zeit.edit.LightBoxForm.extend({

    __name__: 'zeit.edit.TabbedLightBoxForm',

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        if (!isUndefinedOrNull(self.tabs)) {
            self.tabs.active_tab.view.render();
            return;
        }
        var tab_definitions = MochiKit.DOM.getElementsByTagAndClassName(
                null, 'lightbox-tab-data', self.context_element.parentNode);
        var i = 0;
        self.tabs = new zeit.cms.Tabs(
                self.lightbox.content_box);
        forEach(tab_definitions, function(tab_definition) {
            var tab_id = 'tab-'+i;
            var tab_view = new zeit.cms.View(
                    tab_definition.href, tab_id);
            var tab = new zeit.cms.ViewTab(
                tab_id, tab_definition.title, tab_view);
            self.tabs.add(tab);
            self.events.push(
                MochiKit.Signal.connect(
                    tab_view, 'load', function() {
                    self.form = MochiKit.DOM.getFirstElementByTagAndClassName(
                        'form', null, $(tab_view.target_id));
                    if (!isNull(self.form)) {
                        self.rewire_submit_buttons();
                    }
                    $(tab_view.target_id).__handler__ = self;
                    self.eval_javascript_tags();
                    MochiKit.Signal.signal(self, 'after-reload');
            }));
            if (self.context_element == tab_definition) {
                self.tabs.activate(tab_id);
            }
            i = i + 1;
        });
    }

});
